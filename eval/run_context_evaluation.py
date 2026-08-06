from __future__ import annotations

"""CTX-001 离线结构评测器。

只读取冻结 JSONL 并调用纯 ContextBuilder；不连接 Qdrant、SQLite、网络或 LLM，
也不写入 eval/results。输出刻意省略完整 Prompt 和候选正文。
"""

import argparse
import json
import sys
from dataclasses import fields, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from doc_qa.config import ContextConfig
from doc_qa.context_builder import ContextBuilder
from doc_qa.models import Citation, ContextBuildResult
from doc_qa.qa import OUTPUT_CONTRACT, SYSTEM_POLICIES


DEFAULT_CASES = ROOT / "eval" / "context-engineering-cases.jsonl"
FIXED_NOW = datetime(2026, 8, 6, 1, 30, tzinfo=timezone.utc)
SECTION_LABELS = (
    "[Task]",
    "[Evidence: Qdrant Retrieval Only]",
    "[Conversation Context: Non-evidence]",
    "[Notes: Non-evidence]",
    "[Output Contract]",
)
REQUIRED_CATEGORIES = frozenset(
    {
        "single_document_fact",
        "markdown_locator",
        "multi_turn_reference",
        "history_rag_conflict",
        "note_rag_conflict",
        "note_without_retrieval",
        "document_scope_isolation",
        "over_budget",
        "prompt_injection",
        "no_results",
    }
)


class EvaluationCaseError(ValueError):
    """冻结评测用例格式或期望不合法。"""


def load_cases(path: Path = DEFAULT_CASES) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvaluationCaseError(f"JSON 非法: {path}:{line_number}") from exc
        if not isinstance(item, dict):
            raise EvaluationCaseError(f"评测用例必须是对象: {path}:{line_number}")
        case_id = str(item.get("case_id") or "").strip()
        category = str(item.get("category") or "").strip()
        question = str(item.get("question") or "").strip()
        if not case_id or not category or not question or not isinstance(item.get("expected"), dict):
            raise EvaluationCaseError(f"评测用例缺少必填字段: {path}:{line_number}")
        if case_id in seen_ids:
            raise EvaluationCaseError(f"评测 case_id 重复: {case_id}")
        seen_ids.add(case_id)
        cases.append(item)
    if not cases:
        raise EvaluationCaseError(f"评测集为空: {path}")
    return cases


def _repeat_text(item: Mapping[str, Any], key: str) -> str:
    value = str(item.get(key) or "")
    repeat_count = item.get("content_repeat", 1)
    if not isinstance(repeat_count, int) or isinstance(repeat_count, bool) or repeat_count < 1:
        raise EvaluationCaseError("content_repeat 必须是大于 0 的整数")
    return value * repeat_count if key in {"content", "answer"} else value


def _citations(case: Mapping[str, Any]) -> list[Citation]:
    citations: list[Citation] = []
    for raw in case.get("rag_citations", []):
        if not isinstance(raw, Mapping):
            raise EvaluationCaseError("rag_citations 项必须是对象")
        try:
            citations.append(
                Citation(
                    citation_id=str(raw["citation_id"]),
                    document_id=str(raw["document_id"]),
                    document_name=str(raw["document_name"]),
                    chunk_id=str(raw["chunk_id"]),
                    section=str(raw["section"]),
                    page_start=int(raw["page_start"]) if raw.get("page_start") is not None else None,
                    page_end=int(raw["page_end"]) if raw.get("page_end") is not None else None,
                    source_locator=str(raw["source_locator"]),
                    score=float(raw.get("score", 0.5)),
                    content=_repeat_text(raw, "content"),
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise EvaluationCaseError("rag_citations 字段非法") from exc
    return citations


def _expanded_items(case: Mapping[str, Any], key: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for raw in case.get(key, []):
        if not isinstance(raw, Mapping):
            raise EvaluationCaseError(f"{key} 项必须是对象")
        item = dict(raw)
        if "content" in item:
            item["content"] = _repeat_text(raw, "content")
        if "answer" in item:
            item["answer"] = _repeat_text(raw, "answer")
        item.pop("content_repeat", None)
        items.append(item)
    return items


def _config(case: Mapping[str, Any]) -> ContextConfig:
    overrides = case.get("config_overrides", {})
    if not isinstance(overrides, Mapping):
        raise EvaluationCaseError("config_overrides 必须是对象")
    valid_names = {item.name for item in fields(ContextConfig)}
    unknown = set(overrides) - valid_names
    if unknown:
        raise EvaluationCaseError(f"未知 ContextConfig 字段: {sorted(unknown)}")
    return replace(ContextConfig(), **dict(overrides))


def select_final_citation_ids(
    model_source_ids: Sequence[object], included_citation_ids: Sequence[str]
) -> tuple[str, ...]:
    """复现 QA 的引用白名单与空交集回退，不接受非 Evidence 来源。"""
    included = tuple(included_citation_ids)
    included_set = set(included)
    selected = tuple(
        dict.fromkeys(
            str(source_id)
            for source_id in model_source_ids
            if isinstance(source_id, str) and source_id in included_set
        )
    )
    return selected or included


def _fixed_sections(result: ContextBuildResult) -> bool:
    positions = [result.user_prompt.find(label) for label in SECTION_LABELS]
    return result.system_prompt.startswith("[Role & Policies]") and all(
        position >= 0 for position in positions
    ) and positions == sorted(positions)


def _metadata(citations: Iterable[Citation]) -> list[dict[str, Any]]:
    return [
        {
            "citation_id": item.citation_id,
            "document_id": item.document_id,
            "chunk_id": item.chunk_id,
            "source_locator": item.source_locator,
            "score": item.score,
        }
        for item in citations
    ]


def evaluate_case(case: Mapping[str, Any]) -> dict[str, Any]:
    expected = case.get("expected")
    if not isinstance(expected, Mapping):
        raise EvaluationCaseError("expected 必须是对象")
    citations = _citations(case)
    retrieval_ids = tuple(item.citation_id for item in citations)
    expected_status = str(expected.get("status") or "built")

    if not citations:
        status = "no_results"
        fact_source_verdict = "no_evidence_no_answer"
        final_ids: tuple[str, ...] = ()
        checks = {
            "status": status == expected_status,
            "no_prompt_without_evidence": True,
            "citation_selection": list(final_ids) == list(expected.get("final_citation_ids", [])),
            "fact_source": fact_source_verdict == expected.get("fact_source_verdict"),
        }
        return {
            "case_id": case["case_id"],
            "category": case["category"],
            "status": status,
            "builder_invoked": False,
            "retrieval_hits": [],
            "included_citation_ids": [],
            "final_citation_ids": [],
            "selected_packet_ids": [],
            "dropped_packet_ids": [],
            "drop_reasons": {},
            "section_usage": {},
            "total_chars": 0,
            "total_estimated_tokens": 0,
            "compression_events": [],
            "fact_source_verdict": fact_source_verdict,
            "automatic_checks": checks,
            "automatic_verdict": "pass" if all(checks.values()) else "fail",
            "human_review": {
                "required": bool(expected.get("human_review", True)),
                "verdict": "pending",
                "scope": "真实回答的语义正确性与拒答措辞",
            },
        }

    config = _config(case)
    result = ContextBuilder(config, now_provider=lambda: FIXED_NOW).build(
        question=str(case["question"]),
        rag_citations=citations,
        conversation_history=_expanded_items(case, "conversation_history"),
        notes=_expanded_items(case, "notes"),
        system_policies=SYSTEM_POLICIES,
        output_contract=OUTPUT_CONTRACT,
        document_id=str(case.get("document_id") or "").strip() or None,
    )
    included_ids = tuple(result.included_citation_ids)
    final_ids = select_final_citation_ids(case.get("model_source_ids", []), included_ids)
    citation_by_id = {item.citation_id: item for item in citations}
    included_documents = {
        citation_by_id[source_id].document_id
        for source_id in included_ids
        if source_id in citation_by_id
    }
    target_document = str(case.get("document_id") or "").strip() or None
    evidence_pure = set(included_ids).issubset(retrieval_ids) and set(final_ids).issubset(included_ids)
    scope_valid = not target_document or included_documents.issubset({target_document})
    complete_prompt = f"{result.system_prompt}\n\n{result.user_prompt}"
    required_strings = [str(value) for value in expected.get("required_prompt_substrings", [])]
    expected_compression = bool(expected.get("requires_compression", False))
    fact_source_verdict = (
        "qdrant_evidence_only" if evidence_pure and scope_valid else "invalid_non_evidence_source"
    )
    checks = {
        "status": expected_status == "built",
        "citation_selection": list(included_ids) == list(expected.get("included_citation_ids", [])),
        "final_citation_whitelist": list(final_ids) == list(expected.get("final_citation_ids", [])),
        "excluded_citations": not (
            set(expected.get("excluded_citation_ids", [])) & (set(included_ids) | set(final_ids))
        ),
        "required_packets_selected": set(expected.get("required_selected_packet_ids", [])).issubset(
            result.selected_packet_ids
        ),
        "required_packets_dropped": set(expected.get("required_dropped_packet_ids", [])).issubset(
            result.dropped_packet_ids
        ),
        "fact_source_purity": evidence_pure,
        "document_scope": scope_valid,
        "fixed_sections": _fixed_sections(result),
        "prompt_contract_markers": all(value in complete_prompt for value in required_strings),
        "character_budget": result.total_chars <= config.max_input_chars,
        "token_budget": result.total_estimated_tokens <= config.max_input_tokens,
        "stable_compression": bool(result.compression_events) == expected_compression,
        "fact_source": fact_source_verdict == expected.get("fact_source_verdict"),
    }
    return {
        "case_id": case["case_id"],
        "category": case["category"],
        "status": "built",
        "builder_invoked": True,
        "retrieval_hits": _metadata(citations),
        "included_citation_ids": list(included_ids),
        "final_citation_ids": list(final_ids),
        "selected_packet_ids": list(result.selected_packet_ids),
        "dropped_packet_ids": list(result.dropped_packet_ids),
        "drop_reasons": dict(result.drop_reasons),
        "section_usage": {name: dict(usage) for name, usage in result.section_usage.items()},
        "total_chars": result.total_chars,
        "total_estimated_tokens": result.total_estimated_tokens,
        "compression_events": list(result.compression_events),
        "fact_source_verdict": fact_source_verdict,
        "automatic_checks": checks,
        "automatic_verdict": "pass" if all(checks.values()) else "fail",
        "human_review": {
            "required": bool(expected.get("human_review", True)),
            "verdict": "pending",
            "scope": "真实回答语义、冲突裁决与提示注入抵抗",
        },
    }


def run_evaluation(cases: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    results = [evaluate_case(case) for case in cases]
    categories = {str(case["category"]) for case in cases}
    coverage_complete = categories == REQUIRED_CATEGORIES
    passed = sum(result["automatic_verdict"] == "pass" for result in results)
    summary = {
        "schema_version": "ctx-001-step5-v1",
        "mode": "offline_read_only",
        "case_count": len(results),
        "automatic_passed": passed,
        "automatic_failed": len(results) - passed,
        "coverage_complete": coverage_complete,
        "human_review_pending": sum(result["human_review"]["required"] for result in results),
        "external_services_called": False,
        "wrote_result_files": False,
    }
    return {"summary": summary, "cases": results}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="运行 CTX-001 离线上下文结构评测")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES, help="冻结 JSONL 路径")
    args = parser.parse_args(argv)
    report = run_evaluation(load_cases(args.cases))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    summary = report["summary"]
    return 0 if summary["automatic_failed"] == 0 and summary["coverage_complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
