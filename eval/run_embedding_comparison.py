from __future__ import annotations

"""Run the reproducible Phase 6 comparison against the real PDF.

This runner intentionally keeps v3 and v4 in separate Qdrant collections.  It
uses the production ingestion, retrieval, and DeepSeek services, while the
grading helpers are deliberately heuristic and are marked as such in the
result files.  Human review remains the final quality gate.
"""

import argparse
import hashlib
import json
import math
import re
import sys
import time
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from doc_qa.chunker import PageAwareChunker
from doc_qa.config import Settings
from doc_qa.deepseek import DeepSeekChatProvider
from doc_qa.embedding import DashScopeEmbeddingProvider
from doc_qa.ingestion import DocumentIngestionService
from doc_qa.pdf_parser import PdfParser
from doc_qa.qdrant_index import QdrantIndexer
from doc_qa.qa import QuestionAnswerService


V4_MODEL = "text-embedding-v4"
V3_MODEL = "text-embedding-v3"
DIMENSION = 1024
V3_COLLECTION = "docqa_text-embedding-v3_dim1024_eval"
V4_COLLECTION = "docqa_text-embedding-v4_dim1024"
DEFAULT_TOP_K = 5
DEFAULT_THRESHOLD = 0.45
EMBED_PRICE_RMB_PER_1K = 0.0005
DEEPSEEK_INPUT_PRICE_RMB_PER_MILLION = 1.0
DEEPSEEK_OUTPUT_PRICE_RMB_PER_MILLION = 2.0


def load_questions(path: Path) -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"invalid JSON at {path}:{line_number}") from exc
        if not isinstance(item, dict) or not item.get("id") or not item.get("question"):
            raise RuntimeError(f"invalid evaluation item at {path}:{line_number}")
        questions.append(item)
    if not questions:
        raise RuntimeError(f"evaluation set is empty: {path}")
    return questions


def page_hint(source_hint: str) -> list[int] | None:
    if not source_hint:
        return None
    pages: list[int] = []
    for start, end in re.findall(r"第\s*(\d+)\s*(?:-|–|—|至)\s*(\d+)\s*页", source_hint):
        pages.extend(range(int(start), int(end) + 1))
    for value in re.findall(r"第\s*(\d+)\s*页", source_hint):
        if int(value) not in pages:
            pages.append(int(value))
    return sorted(set(pages)) or None


def compact_text(value: str, max_chars: int = 320) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    return value if len(value) <= max_chars else value[:max_chars] + "…"


def text_matches(needle: str, haystack: str) -> bool:
    needle = re.sub(r"\s+", "", needle or "").lower()
    haystack = re.sub(r"\s+", "", haystack or "").lower()
    if not needle:
        return False
    return needle in haystack


def refusal_like(answer: str) -> bool:
    answer = answer or ""
    return any(
        marker in answer
        for marker in (
            "不足以回答",
            "无法回答",
            "不能回答",
            "没有足够",
            "未提供",
            "未提及",
            "未找到",
            "没有提到",
            "文档中没有",
        )
    )


def grade_item(question: dict[str, Any], answer: dict[str, Any]) -> dict[str, Any]:
    expected = [str(item) for item in question.get("expected_answer_points", [])]
    citations = answer.get("citations", [])
    citation_text = "\n".join(str(item.get("content", "")) for item in citations)
    answer_text = str(answer.get("answer", ""))
    point_hits = [point for point in expected if text_matches(point, citation_text + "\n" + answer_text)]
    expected_pages = page_hint(str(question.get("source_hint", "")))
    citation_pages = {
        page
        for citation in citations
        for page in range(int(citation.get("page_start", 0)), int(citation.get("page_end", 0)) + 1)
    }
    is_out_of_doc = any(
        marker in str(question.get("question_type", ""))
        for marker in ("文档外", "无答案", "拒答", "安全")
    ) or question.get("id") in {"q014", "q015", "q020"}
    if expected_pages:
        source_accuracy: bool | None = bool(citation_pages.intersection(expected_pages))
    else:
        source_accuracy = bool(citations)
    if is_out_of_doc:
        answer_correct = refusal_like(answer_text)
        hallucination = not answer_correct
    else:
        answer_correct = bool(expected) and len(point_hits) >= max(1, math.ceil(len(expected) * 0.5))
        hallucination = False
    return {
        "retrieval_hit": bool(citations),
        "source_accuracy": source_accuracy,
        "answer_point_hits": point_hits,
        "answer_point_coverage": (len(point_hits) / len(expected)) if expected else None,
        "answer_correct_auto": answer_correct,
        "hallucination_flag_auto": hallucination,
        "readability_auto": bool(answer_text.strip()) if answer.get("status") == "answered" else True,
    }


class CallMetrics:
    def __init__(self) -> None:
        self.logical_embedding_calls = 0
        self.embedding_api_calls = 0
        self.embedding_input_chars = 0
        self.logical_chat_calls = 0
        self.chat_api_calls = 0
        self.chat_input_tokens = 0
        self.chat_output_tokens = 0

    @property
    def embedding_retries(self) -> int:
        return max(0, self.embedding_api_calls - self.logical_embedding_calls)

    @property
    def chat_retries(self) -> int:
        return max(0, self.chat_api_calls - self.logical_chat_calls)


def instrument_embedding(provider: DashScopeEmbeddingProvider, metrics: CallMetrics) -> None:
    original_encode = provider._client.encode

    def counted_encode(texts: list[str], *args: Any, **kwargs: Any) -> Any:
        metrics.embedding_api_calls += 1
        metrics.embedding_input_chars += sum(len(str(text)) for text in texts)
        return original_encode(texts, *args, **kwargs)

    provider._client.encode = counted_encode
    original_provider_encode = provider.encode

    def counted_provider_encode(texts: list[str]) -> Any:
        metrics.logical_embedding_calls += math.ceil(len(texts) / provider.batch_size)
        return original_provider_encode(texts)

    provider.encode = counted_provider_encode


def _usage_value(usage: Any, *names: str) -> int:
    for name in names:
        value = getattr(usage, name, None)
        if isinstance(value, int):
            return value
        if isinstance(usage, dict) and isinstance(usage.get(name), int):
            return int(usage[name])
    return 0


def instrument_chat(provider: DeepSeekChatProvider, metrics: CallMetrics) -> None:
    original_create = provider._client.chat.completions.create

    def counted_create(*args: Any, **kwargs: Any) -> Any:
        metrics.chat_api_calls += 1
        response = original_create(*args, **kwargs)
        usage = getattr(response, "usage", None)
        metrics.chat_input_tokens += _usage_value(usage, "prompt_tokens", "input_tokens")
        metrics.chat_output_tokens += _usage_value(usage, "completion_tokens", "output_tokens")
        return response

    provider._client.chat.completions.create = counted_create


def build_provider(settings: Settings, model: str, metrics: CallMetrics) -> DashScopeEmbeddingProvider:
    provider = DashScopeEmbeddingProvider(
        model_name=model,
        expected_dimension=DIMENSION,
        api_key=settings.embedding_api_key,
        base_url=settings.embedding_base_url,
        batch_size=settings.embedding_batch_size,
        max_retries=settings.embedding_max_retries,
        retry_backoff_seconds=settings.embedding_retry_backoff_seconds,
    )
    instrument_embedding(provider, metrics)
    return provider


def build_indexer(settings: Settings, collection: str) -> QdrantIndexer:
    return QdrantIndexer(
        collection,
        DIMENSION,
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        local_path=settings.qdrant_local_path,
        timeout=settings.qdrant_timeout,
    )


def collection_snapshot(indexer: QdrantIndexer, expected_chunks: set[str]) -> dict[str, Any]:
    indexer.ensure_collection()
    return {
        "collection": indexer.collection_name,
        "dimension": indexer._collection_dimension(),
        "points_count": indexer.point_count(),
        "metadata_complete": indexer.verify_metadata(expected_chunks),
    }


def ensure_v3_index(
    settings: Settings,
    pdf: Path,
    chunks: list[Any],
    provider: DashScopeEmbeddingProvider,
) -> tuple[QdrantIndexer, dict[str, Any]]:
    indexer = build_indexer(settings, V3_COLLECTION)
    expected_ids = {chunk.chunk_id for chunk in chunks}
    try:
        indexer.ensure_collection()
        current = indexer.point_count()
        if current not in (0, len(chunks)):
            raise RuntimeError(
                f"v3 collection is partial ({current}/{len(chunks)} points); "
                "refusing to delete or repair it automatically"
            )
        if current == 0:
            vectors = provider.encode([chunk.content for chunk in chunks])
            indexer.upsert(chunks, vectors)
        snapshot = collection_snapshot(indexer, expected_ids)
        if snapshot["points_count"] != len(chunks) or not snapshot["metadata_complete"]:
            raise RuntimeError(f"v3 collection verification failed: {snapshot}")
        snapshot["indexed_now"] = current == 0
        snapshot["document_id"] = chunks[0].document_id
        snapshot["document_name"] = pdf.name
        return indexer, snapshot
    except Exception:
        indexer.close()
        raise


def answer_one(
    qa: QuestionAnswerService,
    question: dict[str, Any],
    metrics: CallMetrics,
) -> dict[str, Any]:
    started = time.perf_counter()
    metrics.logical_chat_calls += 1
    try:
        response = qa.ask(str(question["question"]))
        result = response.as_dict()
        result["citations"] = [
            {key: value for key, value in citation.items() if key != "content"}
            | {"content": compact_text(str(citation.get("content", "")))}
            for citation in result.get("citations", [])
        ]
        result["failure_reason"] = None
        result["status"] = response.status
    except Exception as exc:
        result = {
            "status": "failed",
            "question": str(question["question"]),
            "answer": "",
            "citations": [],
            "retrieved_count": 0,
            "model": qa.chat.model_name,
            "failure_reason": f"{type(exc).__name__}: {str(exc)}",
        }
    result["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
    result.update(grade_item(question, result))
    return result


def run_model(
    settings: Settings,
    model: str,
    collection: str,
    questions: list[dict[str, Any]],
    v3_indexing_metrics: CallMetrics | None = None,
) -> dict[str, Any]:
    metrics = CallMetrics()
    provider = build_provider(settings, model, metrics)
    indexer = build_indexer(settings, collection)
    chat = DeepSeekChatProvider(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        model_name=settings.deepseek_model,
        thinking=settings.deepseek_thinking,
        trust_env=settings.deepseek_trust_env,
        max_retries=settings.deepseek_max_retries,
        retry_backoff_seconds=settings.deepseek_retry_backoff_seconds,
    )
    instrument_chat(chat, metrics)
    qa_settings = replace(
        settings,
        embedding_model=model,
        embedding_dimension=DIMENSION,
        retrieval_top_k=DEFAULT_TOP_K,
        retrieval_score_threshold=DEFAULT_THRESHOLD,
    )
    qa = QuestionAnswerService(settings=qa_settings, query_embedding=provider, chat=chat, indexer=indexer)
    rows: list[dict[str, Any]] = []
    try:
        for question in questions:
            row = answer_one(qa, question, metrics)
            row = {
                "id": question["id"],
                "question": question["question"],
                "question_type": question.get("question_type"),
                "expected_answer_points": question.get("expected_answer_points", []),
                "source_document": question.get("source_document"),
                "source_hint": question.get("source_hint"),
                "expected_pages": page_hint(str(question.get("source_hint", ""))),
                **row,
            }
            rows.append(row)
    finally:
        indexer.close()
        chat._http_client.close()
    latencies = [float(row["latency_ms"]) for row in rows]
    answered = [row for row in rows if row["status"] == "answered"]
    metrics_embedding_tokens = max(1, math.ceil(metrics.embedding_input_chars / 1.5))
    return {
        "model": model,
        "dimension": DIMENSION,
        "collection": collection,
        "top_k": DEFAULT_TOP_K,
        "score_threshold": DEFAULT_THRESHOLD,
        "rows": rows,
        "metrics": {
            "question_count": len(rows),
            "answered_count": len(answered),
            "no_results_count": sum(row["status"] == "no_results" for row in rows),
            "failed_count": sum(row["status"] == "failed" for row in rows),
            "retrieval_hit_rate": sum(bool(row["retrieval_hit"]) for row in rows) / len(rows),
            "source_accuracy_rate_auto": sum(bool(row["source_accuracy"]) for row in rows) / len(rows),
            "answer_correct_rate_auto": sum(bool(row["answer_correct_auto"]) for row in rows) / len(rows),
            "refusal_accuracy_rate_auto": sum(
                bool(row["answer_correct_auto"])
                for row in rows
                if any(marker in str(row["question_type"]) for marker in ("文档外", "无答案", "拒答", "安全"))
                or row["id"] in {"q014", "q015", "q020"}
            ) / max(
                1,
                sum(
                    any(marker in str(row["question_type"]) for marker in ("文档外", "无答案", "拒答", "安全"))
                    or row["id"] in {"q014", "q015", "q020"}
                    for row in rows
                ),
            ),
            "average_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0,
            "embedding_logical_calls": metrics.logical_embedding_calls,
            "embedding_api_calls": metrics.embedding_api_calls,
            "embedding_retries": metrics.embedding_retries,
            "embedding_input_chars": metrics.embedding_input_chars,
            "embedding_input_tokens_estimate": metrics_embedding_tokens,
            "chat_logical_calls": metrics.logical_chat_calls,
            "chat_api_calls": metrics.chat_api_calls,
            "chat_retries": metrics.chat_retries,
            "deepseek_input_tokens": metrics.chat_input_tokens,
            "deepseek_output_tokens": metrics.chat_output_tokens,
            "embedding_cost_estimate_rmb": round(metrics_embedding_tokens / 1000 * EMBED_PRICE_RMB_PER_1K, 6),
            "deepseek_cost_estimate_rmb": round(
                metrics.chat_input_tokens / 1_000_000 * DEEPSEEK_INPUT_PRICE_RMB_PER_MILLION
                + metrics.chat_output_tokens / 1_000_000 * DEEPSEEK_OUTPUT_PRICE_RMB_PER_MILLION,
                6,
            ),
        },
    }


def safe_json_for_report(result: dict[str, Any]) -> dict[str, Any]:
    return result


def make_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Embedding v3/v4 Phase 6 对比评测报告",
        "",
        f"- 评测时间：`{summary['environment']['started_at']}`",
        f"- 测试文档：`{summary['environment']['pdf_name']}`",
        f"- 页数/分块：`{summary['environment']['page_count']}` / `{summary['environment']['chunk_count']}`",
        f"- 评测问题：`{summary['environment']['question_count']}` 条",
        "- 自动评分仅用于可复现初筛，最终质量仍需人工复核。",
        "",
        "## 模型与集合",
        "",
        "| 模型 | 维度 | Collection | Recall/检索命中率 | 来源准确率（自动） | 回答正确率（自动） | 拒答准确率（自动） | 平均耗时 |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for model_name, result in summary["models"].items():
        metrics = result["metrics"]
        lines.append(
            f"| {model_name} | {result['dimension']} | `{result['collection']}` | "
            f"{metrics['retrieval_hit_rate']:.1%} | {metrics['source_accuracy_rate_auto']:.1%} | "
            f"{metrics['answer_correct_rate_auto']:.1%} | {metrics['refusal_accuracy_rate_auto']:.1%} | "
            f"{metrics['average_latency_ms']:.0f} ms |"
        )
    lines.extend(
        [
            "",
            "## 调用、失败与成本",
            "",
            "成本是估算值：Embedding 按普通文本输入价格 0.0005 元/千 token；DeepSeek 使用记录到的 usage，按 cache miss 输入 1 元/百万 token、输出 2 元/百万 token 的保守假设计算。",
            "",
            "| 模型 | Embedding API 调用/重试 | DeepSeek API 调用/重试 | 失败题数 | Embedding 估算成本 | DeepSeek 估算成本 |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for model_name, result in summary["models"].items():
        metrics = result["metrics"]
        lines.append(
            f"| {model_name} | {metrics['embedding_api_calls']}/{metrics['embedding_retries']} | "
            f"{metrics['chat_api_calls']}/{metrics['chat_retries']} | {metrics['failed_count']} | "
            f"¥{metrics['embedding_cost_estimate_rmb']:.6f} | ¥{metrics['deepseek_cost_estimate_rmb']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## 自动评分说明",
            "",
            "- `retrieval_hit`：Top-K 是否返回来源；",
            "- `source_accuracy`：依据评测集页码提示与返回页码交集；没有页码提示时只检查是否有来源；",
            "- `answer_point_coverage`：期望答案要点的简单文本命中率；",
            "- 文档外/无答案/拒答题要求出现明确拒答表达；返回的检索片段仍需人工核对是否相关；",
            "- 这些规则不能替代人工判断，尤其不能单独证明回答事实正确。",
            "",
            "## Collection 隔离证据",
            "",
            f"- 评测前 v4：`{summary['collections_before'][V4_COLLECTION]}`",
            f"- 评测后 v4：`{summary['collections_after'][V4_COLLECTION]}`",
            f"- v3：`{summary['collections_after'][V3_COLLECTION]}`",
            "- v3 与 v4 使用独立 collection，未混用向量。",
            "",
            "## 人工复核建议",
            "",
            "优先复核：跨章节归纳、多轮追问、文档外问题、来源页码、中文术语和分块边界题。只有人工核验通过后，才可将自动评分作为最终选型依据。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, default=ROOT / "data/reference/Happy-LLM-0727.pdf")
    parser.add_argument("--questions", type=Path, default=ROOT / "eval/questions.jsonl")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "eval/results")
    args = parser.parse_args()
    started_at = datetime.now(timezone.utc).isoformat()
    settings = Settings.from_env(ROOT / ".env")
    if settings.embedding_model != V4_MODEL or settings.embedding_dimension != DIMENSION:
        raise RuntimeError(
            f"Phase 6 requires configured v4/1024 baseline, got {settings.embedding_model}/{settings.embedding_dimension}"
        )
    if settings.qdrant_url != "http://localhost:6333":
        raise RuntimeError(f"expected local Docker Qdrant URL, got {settings.qdrant_url!r}")
    if not settings.embedding_api_key or not settings.deepseek_api_key:
        raise RuntimeError("EMBED_API_KEY and DEEPSEEK_API_KEY must be configured locally")
    if not args.pdf.exists():
        raise RuntimeError(f"benchmark PDF not found: {args.pdf}")

    questions = load_questions(args.questions)
    parser_impl = PdfParser()
    document_id, pages = parser_impl.parse(args.pdf)
    chunks = PageAwareChunker(settings.chunk_size, settings.chunk_overlap).chunk(
        document_id, args.pdf.name, args.pdf, pages
    )
    if not chunks or any(not chunk.content.strip() for chunk in chunks):
        raise RuntimeError("benchmark PDF produced empty chunks")
    expected_ids = {chunk.chunk_id for chunk in chunks}
    v4_indexer = build_indexer(settings, V4_COLLECTION)
    try:
        before_v4 = collection_snapshot(v4_indexer, expected_ids)
    finally:
        v4_indexer.close()
    if before_v4["dimension"] != DIMENSION or before_v4["points_count"] != len(chunks):
        raise RuntimeError(f"v4 baseline collection is not ready: {before_v4}; expected {len(chunks)} points")
    if not before_v4["metadata_complete"]:
        raise RuntimeError("v4 baseline metadata is incomplete")

    v3_metrics = CallMetrics()
    v3_provider = build_provider(settings, V3_MODEL, v3_metrics)
    v3_indexer, v3_snapshot = ensure_v3_index(settings, args.pdf, chunks, v3_provider)
    v3_indexer.close()

    v4_result = run_model(settings, V4_MODEL, V4_COLLECTION, questions)
    v3_result = run_model(settings, V3_MODEL, V3_COLLECTION, questions)
    v3_result["indexing_metrics"] = {
        "embedding_api_calls": v3_metrics.embedding_api_calls,
        "embedding_retries": v3_metrics.embedding_retries,
        "embedding_input_chars": v3_metrics.embedding_input_chars,
        "collection_indexed_now": v3_snapshot["indexed_now"],
    }
    after_v4_indexer = build_indexer(settings, V4_COLLECTION)
    after_v3_indexer = build_indexer(settings, V3_COLLECTION)
    try:
        after_v4 = collection_snapshot(after_v4_indexer, expected_ids)
        after_v3 = collection_snapshot(after_v3_indexer, expected_ids)
    finally:
        after_v4_indexer.close()
        after_v3_indexer.close()

    summary = {
        "schema_version": "phase6-embedding-comparison-v1",
        "environment": {
            "started_at": started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "pdf_name": args.pdf.name,
            "pdf_sha256": hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
            "page_count": len(pages),
            "chunk_count": len(chunks),
            "question_count": len(questions),
            "embedding_batch_size": settings.embedding_batch_size,
            "top_k": DEFAULT_TOP_K,
            "score_threshold": DEFAULT_THRESHOLD,
            "deepseek_model": settings.deepseek_model,
            "qdrant_url": settings.qdrant_url,
            "token_estimate_method": "ceil(UTF-8 text character count / 1.5) when provider usage is unavailable",
        },
        "collections_before": {V4_COLLECTION: before_v4},
        "collections_after": {V4_COLLECTION: after_v4, V3_COLLECTION: after_v3},
        "models": {V3_MODEL: v3_result, V4_MODEL: v4_result},
        "selection": {
            "default_model": V4_MODEL,
            "decision_status": "pending_human_review",
            "reason": "Both models were evaluated with the same questions; automatic heuristics are not sufficient for final selection.",
        },
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "embedding-v3-v4-summary.json").write_text(
        json.dumps(safe_json_for_report(summary), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (args.output_dir / "embedding-v3-v4-report.md").write_text(make_report(summary), encoding="utf-8")
    print(json.dumps({"status": "completed", "summary": str(args.output_dir / "embedding-v3-v4-summary.json")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
