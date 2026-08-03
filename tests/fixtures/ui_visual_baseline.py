"""Deterministic browser fixture for the frozen UI visual baselines.

The fixture uses the real Gradio app, UIController, SQLite store, learning
service, session persistence, citation models, and note callbacks. It replaces
only the external QA provider so visual verification never needs production
credentials, production SQLite, or production Qdrant points.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

from doc_qa.config import Settings
from doc_qa.learning import LearningService
from doc_qa.models import AnswerResponse, Citation
from doc_qa.ui import UIController, build_app


PDF_DOCUMENT_ID = "fixture-pdf-happy-llm"
MARKDOWN_DOCUMENT_ID = "fixture-markdown-multidocument"


class VisualBaselineQA:
    """Deterministic external-service substitute at the existing QA boundary."""

    model_name = "ui-visual-baseline"

    def ask(
        self,
        question: str,
        *,
        document_id: str | None = None,
        conversation_context: list[dict[str, str]] | None = None,
    ) -> AnswerResponse:
        del conversation_context
        citations = [
            Citation(
                citation_id="baseline-pdf-page-6",
                document_id=PDF_DOCUMENT_ID,
                document_name="Happy-LLM-0727.pdf",
                chunk_id="pdf-page-6-chunk-1",
                section="",
                page_start=6,
                page_end=6,
                source_locator="Happy-LLM-0727.pdf#page=6&chunk=pdf-page-6-chunk-1",
                score=0.93,
                content="该 PDF 片段对应第 6 页，用于验证页码来源卡和原始引用入口。",
            ),
            Citation(
                citation_id="baseline-markdown-section-3",
                document_id=MARKDOWN_DOCUMENT_ID,
                document_name="phase3-multidocument-guide.md",
                chunk_id="markdown-section-3-paragraph-2",
                section="第 3 章",
                page_start=None,
                page_end=None,
                source_locator=(
                    "phase3-multidocument-guide.md#section=%E7%AC%AC3%E7%AB%A0"
                    "&paragraph=2&lines=11-14&chunk=markdown-section-3-paragraph-2"
                ),
                score=0.89,
                content="该 Markdown 片段保留章节、段落和行号定位，用于验证来源语义。",
            ),
        ]
        if document_id:
            citations = [item for item in citations if item.document_id == document_id]
        if not citations:
            return AnswerResponse(
                status="no_results",
                question=question,
                answer="当前文档范围没有足够依据回答这个问题。",
                citations=[],
                retrieved_count=0,
                model=self.model_name,
            )
        return AnswerResponse(
            status="answered",
            question=question,
            answer="建议先理解整体架构，再按“解析 → 检索 → 生成 → 评估”的顺序推进，并逐步回到原文核对。",
            citations=citations,
            retrieved_count=len(citations),
            model=self.model_name,
        )


def seed_documents(controller: UIController) -> None:
    controller.store.upsert_document(
        document_id=PDF_DOCUMENT_ID,
        document_name="Happy-LLM-0727.pdf",
        source_path="fixture/Happy-LLM-0727.pdf",
        pages_with_text=171,
        chunk_count=262,
        indexed_point_count=262,
        status="indexed",
        content_hash="fixture-pdf-content-hash",
        source_locator_scheme="pdf-page-v1",
    )
    controller.store.upsert_document(
        document_id=MARKDOWN_DOCUMENT_ID,
        document_name="phase3-multidocument-guide.md",
        source_path="fixture/phase3-multidocument-guide.md",
        source_unit_count=5,
        chunk_count=14,
        indexed_point_count=14,
        status="indexed",
        format="markdown",
        content_hash="fixture-markdown-content-hash",
        source_locator_scheme="markdown-heading-line-v1",
    )
    controller.store.upsert_document(
        document_id="fixture-markdown-archived",
        document_name="RAG 评测笔记.md",
        source_path="fixture/rag-evaluation-notes.md",
        source_unit_count=3,
        chunk_count=12,
        indexed_point_count=12,
        status="archived",
        format="markdown",
        content_hash="fixture-archived-content-hash",
        source_locator_scheme="markdown-heading-line-v1",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch the isolated Agent3 UI visual baseline fixture.")
    parser.add_argument("--port", type=int, default=7865)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    runtime_parent = project_root / "output" / "ui-visual-baseline-runtime"
    runtime_parent.mkdir(parents=True, exist_ok=True)

    with TemporaryDirectory(prefix="run-", dir=runtime_parent) as runtime:
        runtime_root = Path(runtime)
        settings = Settings(
            sqlite_path=runtime_root / "baseline.sqlite3",
            qdrant_url=None,
            qdrant_local_path=runtime_root / "qdrant",
        )
        controller = UIController(settings)
        seed_documents(controller)
        controller._learning = LearningService(  # fixture-only injection at the existing service boundary
            settings,
            qa_service=VisualBaselineQA(),
            store=controller.store,
        )
        try:
            build_app(controller).launch(
                server_name="127.0.0.1",
                server_port=args.port,
                share=False,
                show_error=True,
                quiet=True,
            )
        finally:
            controller.close()


if __name__ == "__main__":
    main()
