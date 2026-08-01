from __future__ import annotations

from pathlib import Path

from doc_qa.config import Settings
from doc_qa.models import IndexReport
from doc_qa.ui import APP_CSS, UIController, build_app


def test_gradio_app_builds_without_external_services(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui.sqlite3"))
    demo = build_app(controller)
    assert len(demo.blocks) >= 40
    controller.close()


def test_ui_initial_state_creates_session_and_empty_library(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui.sqlite3"))
    session_id, status, history, sources, documents, stats = controller.initialize()
    assert session_id.startswith("session_")
    assert "已创建学习会话" in status
    assert history == []
    assert sources == {}
    assert documents == []
    assert stats["question_count"] == 0
    controller.close()


def test_ui_rejects_unsupported_upload_without_calling_services(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui.sqlite3"))
    status, documents, dropdown = controller.index_document("notes.txt")
    assert "仅支持 PDF" in status
    assert documents == []
    assert dropdown["choices"][0] == ("全部文档", "")
    controller.close()


def test_ui_accepts_markdown_and_renders_format_and_locator(tmp_path: Path):
    source = tmp_path / "notes.md"
    source.write_text("# Notes\n\n学习材料。\n", encoding="utf-8")
    controller = UIController(Settings(sqlite_path=tmp_path / "ui.sqlite3"))

    class FakeIngestion:
        def index_document(self, path: Path) -> IndexReport:
            return IndexReport(
                status="indexed",
                document_id="doc-md",
                document_name=path.name,
                collection_name="docqa_text-embedding-v4_dim1024",
                embedding_model="text-embedding-v4",
                embedding_dimension=1024,
                pages_with_text=0,
                chunk_count=1,
                existing_chunk_count=0,
                indexed_point_count=1,
                metadata_complete=True,
                idempotent_replay=False,
                source_path=str(path),
            )

    controller._ensure_ingestion = lambda: FakeIngestion()  # type: ignore[method-assign]
    status, documents, dropdown = controller.index_document(str(source))
    assert "索引完成" in status
    assert documents[0][0:5] == ["notes.md", "MARKDOWN", "doc-md", "indexed", "0 个章节/段落单元"]
    assert documents[0][7] == "markdown-heading-line-v1"
    assert ("notes.md · MARKDOWN · indexed", "doc-md") in dropdown["choices"]
    controller.close()


def test_ui_catalog_renders_document_status(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui.sqlite3"))
    controller.store.upsert_document(
        document_id="doc-1",
        document_name="Happy-LLM-0727.pdf",
        source_path="data/reference/Happy-LLM-0727.pdf",
        pages_with_text=171,
        chunk_count=262,
        indexed_point_count=262,
        status="indexed",
    )
    rows = controller.document_rows()
    choices = controller.document_choices()
    assert rows[0][0] == "Happy-LLM-0727.pdf"
    assert rows[0][1:8] == ["PDF", "doc-1", "indexed", "171 页", "262", "262", "pdf-page-v1"]
    assert ("Happy-LLM-0727.pdf · PDF · indexed", "doc-1") in choices
    controller.close()


def test_ui_scope_switch_clears_transient_answer_source_and_note(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui.sqlite3"))
    result = controller.switch_document_scope("doc-md")
    assert "doc-md" in result[0]
    assert result[1] == "等待提问"
    assert result[2] == []
    assert result[3] == {}
    assert result[4] == "暂无可展示的来源。"
    assert result[5] == ""
    assert result[6] == ""
    assert result[7] == []
    assert result[9] == ""
    assert controller._scope_state.document_id == "doc-md"
    assert controller._scope_state.conversation_context == ()
    controller.close()


def test_ui_new_session_clears_source_summary_and_transient_state(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui.sqlite3"))
    result = controller.new_session()
    assert result[2] == []
    assert result[3] == {}
    assert result[4] == "暂无可展示的来源。"
    assert result[5] == "等待提问"
    assert result[6] == ""
    assert result[7] == ""
    assert result[9]["choices"] == []
    assert result[10] == ""
    controller.close()


def test_ui_styles_cover_required_responsive_breakpoints_and_states():
    assert "@media (max-width: 1100px)" in APP_CSS
    assert "@media (max-width: 760px)" in APP_CSS
    assert "docqa-source-summary" in APP_CSS
    assert "loading" not in APP_CSS  # loading is provided by Gradio event state, not fake CSS text
