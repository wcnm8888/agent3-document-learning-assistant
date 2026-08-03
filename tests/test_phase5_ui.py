from __future__ import annotations

from pathlib import Path

from doc_qa.config import Settings
from doc_qa.models import IndexReport
from doc_qa.ui import (
    APP_CSS,
    APP_CSS_PATH,
    APP_JS,
    UIController,
    _format_document_inspector,
    _format_session_timeline,
    _format_source_cards,
    _format_source_summary,
    build_app,
)


def test_gradio_app_builds_without_external_services(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui.sqlite3"))
    demo = build_app(controller)
    assert len(demo.blocks) >= 40
    controller.close()


def test_ui_initial_state_creates_session_and_empty_library(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui.sqlite3"))
    session_id, status, history, sources, documents, stats = controller.initialize()
    assert session_id.startswith("session_")
    assert status == "会话已就绪"
    assert session_id not in status
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


def test_ui_document_table_is_compact_and_details_keep_full_metadata(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui.sqlite3"))
    full_document_id = "a" * 64
    controller.store.upsert_document(
        document_id=full_document_id,
        document_name="A very long document name for the compact library view.md",
        source_path="data/reference/guide.md",
        pages_with_text=0,
        source_unit_count=8,
        chunk_count=4,
        indexed_point_count=4,
        status="indexed",
        format="markdown",
        source_locator_scheme="markdown-heading-line-v1",
    )

    assert controller.document_table_rows() == [[
        "A very long document name for the compact library view.md",
        "MARKDOWN",
        "indexed",
        controller.store.list_documents()[0].updated_at,
    ]]
    details = controller.document_details(full_document_id)
    assert details["document_id"] == full_document_id
    assert details["source_locator_scheme"] == "markdown-heading-line-v1"
    controller.close()


def test_ui_scope_switch_clears_transient_answer_source_and_note(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui.sqlite3"))
    result = controller.switch_document_scope("doc-md")
    assert "doc-md" in result[0]
    assert result[1] == "等待提问"
    assert result[2] == []
    assert result[3] == {}
    assert "docqa-source-empty" in result[4]
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
    assert "docqa-source-empty" in result[4]
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
    assert "--docqa-bg: #09090b" in APP_CSS
    assert "--docqa-accent: #2f80ed" in APP_CSS
    assert "docqa-document-table" in APP_CSS
    assert "loading" not in APP_CSS  # loading is provided by Gradio event state, not fake CSS text


def test_ui4_status_feedback_is_explicit_and_scope_switch_clears_transient_state(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui.sqlite3"))
    session_id, *_ = controller.initialize()

    assert controller.index_document(None)[0].startswith("⚠️")
    assert controller.index_document(str(tmp_path / "notes.txt"))[0].startswith("❌")
    missing_path = tmp_path / "missing.md"
    assert controller.index_document(str(missing_path))[0].startswith("❌")
    empty_path = tmp_path / "empty.md"
    empty_path.write_text("", encoding="utf-8")
    assert controller.index_document(str(empty_path))[0].startswith("❌")
    assert controller.ask(session_id, "", None, [])[2].startswith("⚠️")
    assert controller.save_note(session_id, "", None, "", "draft")[0].startswith("⚠️")
    assert controller.update_note("", "draft", session_id)[0].startswith("⚠️")

    switched = controller.switch_document_scope("doc-md")
    assert "doc-md" in switched[0]
    assert switched[1] == "等待提问"
    assert switched[2] == []
    assert switched[3] == {}
    assert switched[5] == ""
    assert switched[6] == ""
    controller.close()


def test_ui4_styles_cover_focus_disabled_and_semantic_status_rules():
    assert "[role=\"combobox\"]:focus-visible" in APP_CSS
    assert "button:disabled" in APP_CSS
    assert "input:disabled" in APP_CSS
    assert "[aria-disabled=\"true\"]" in APP_CSS
    assert "opacity: 0.55" in APP_CSS


def test_ui_r4_uses_approved_workspace_layers(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui-r4.sqlite3"))
    demo = build_app(controller)

    blocks = demo.blocks.values() if isinstance(demo.blocks, dict) else demo.blocks
    element_ids = {
        getattr(block, "elem_id", None)
        for block in blocks
        if getattr(block, "elem_id", None)
    }
    assert {"library-view", "session-view", "docqa-sidebar", "sources-panel"} <= element_ids
    assert "docqa-library-view" in APP_CSS
    assert "docqa-session-view" in APP_CSS
    assert "docqa-context-tabs" in APP_CSS
    assert "docqa-space-nav" in APP_CSS
    controller.close()


def test_ui_r5_formats_source_cards_and_recent_documents(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui-r5.sqlite3"))
    controller.store.upsert_document(
        document_id="doc-pdf",
        document_name="A very long PDF handbook.pdf",
        source_path="data/reference/handbook.pdf",
        pages_with_text=42,
        chunk_count=3,
        indexed_point_count=3,
        status="indexed",
        format="pdf",
        source_locator_scheme="pdf-page-v1",
    )
    controller.store.upsert_document(
        document_id="doc-md",
        document_name="A very long Markdown guide.md",
        source_path="data/reference/guide.md",
        source_unit_count=8,
        chunk_count=4,
        indexed_point_count=4,
        status="archived",
        format="markdown",
        source_locator_scheme="markdown-heading-line-v1",
    )

    recent = controller.recent_document_rows()
    recent_by_name = {row[0]: row[1] for row in recent}
    assert recent_by_name["A very long Markdown guide.md"] == "MARKDOWN · archived"
    assert recent_by_name["A very long PDF handbook.pdf"] == "PDF · indexed"
    summary = _format_source_summary([
        {
            "citation_id": "src-pdf",
            "document_name": "handbook.pdf",
            "page_start": 6,
            "page_end": 7,
            "source_locator": "handbook.pdf#page=6&chunk=c1",
            "score": 0.91,
            "content": "PDF source excerpt",
        },
        {
            "citation_id": "src-md",
            "document_name": "guide.md",
            "section": "核心章节",
            "source_locator": "guide.md#section=%E6%A0%B8%E5%BF%83%E7%AB%A0%E8%8A%82&paragraph=2&lines=11-14&chunk=c2",
            "score": 0.88,
            "content": "Markdown source excerpt",
        },
    ])
    assert "PDF · 第 6–7 页" in summary
    assert "Markdown · 核心章节 · 段落 2 · 行 11-14" in summary
    assert "handbook.pdf#page=6" in summary
    controller.close()


def test_ui_hf1_renders_real_recent_navigation_markup(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui-hf1.sqlite3"))
    controller.store.upsert_document(
        document_id="doc-hf1",
        document_name="<安全>指南.md",
        source_path="data/reference/guide.md",
        source_unit_count=3,
        chunk_count=2,
        indexed_point_count=2,
        status="indexed",
        format="markdown",
        source_locator_scheme="markdown-heading-line-v1",
    )

    markup = controller.recent_document_markup()
    assert "docqa-recent-item" in markup
    assert "&lt;安全&gt;指南.md" in markup
    assert "MARKDOWN · indexed" in markup
    assert "<安全>指南.md" not in markup
    assert "docqa-topbar-chip" in APP_CSS
    assert "docqa-sidebar-footer" in APP_CSS
    controller.close()


def test_ui_hf2_renders_document_rows_and_full_detail_metadata(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui-hf2.sqlite3"))
    long_name = "一份很长的产品手册与检索指南-用于验证文档行折叠与详情展示.md"
    full_document_id = "hf2-markdown-" + "a" * 48
    controller.store.upsert_document(
        document_id=full_document_id,
        document_name=long_name,
        source_path="data/reference/guide.md",
        content_hash="hash-markdown-hf2",
        source_unit_count=12,
        chunk_count=8,
        indexed_point_count=8,
        status="indexed",
        format="markdown",
        source_locator_scheme="markdown-heading-line-v1",
    )
    controller.store.upsert_document(
        document_id="hf2-failed",
        document_name="失败文档.md",
        source_path="data/reference/failed.md",
        status="failed",
        format="markdown",
        error_message="Embedding API key=secret-value failed",
    )

    markup = controller.document_library_markup()
    assert "docqa-document-list" in markup
    assert "docqa-document-row" in markup
    assert long_name in markup
    assert "已索引" in markup
    assert "索引失败" in markup
    assert "secret-value" not in markup
    assert "API key=[REDACTED]" in markup

    detail = controller.document_detail_summary(full_document_id)
    assert full_document_id in detail
    assert "hash-markdown-hf2" in detail
    assert "markdown-heading-line-v1" in detail
    assert "Qdrant points" in detail
    controller.close()


def test_ui_hf2_builds_document_inspector_contract(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui-hf2-layout.sqlite3"))
    demo = build_app(controller)
    blocks = demo.blocks.values() if isinstance(demo.blocks, dict) else demo.blocks
    element_ids = {
        getattr(block, "elem_id", None)
        for block in blocks
        if getattr(block, "elem_id", None)
    }
    assert {"sources-panel", "document-inspector", "library-view"} <= element_ids
    assert "docqa-document-list" in APP_CSS
    assert "docqa-document-row" in APP_CSS
    assert "docqa-document-inspector" in APP_CSS
    assert "docqa-detail-error" in APP_CSS
    controller.close()


def test_hf_r3_renders_real_document_inspector_for_pdf_and_markdown(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "hf-r3-inspector.sqlite3"))
    controller.store.upsert_document(
        document_id="hf-r3-pdf-" + "p" * 36,
        document_name="一份非常长的 PDF 文档名称，用于检查右侧详情不会丢失元数据.pdf",
        source_path="data/reference/handbook.pdf",
        pages_with_text=171,
        chunk_count=262,
        indexed_point_count=262,
        status="indexed",
        content_hash="pdf-hash-hf-r3",
        source_locator_scheme="pdf-page-v1",
    )
    controller.store.upsert_document(
        document_id="hf-r3-md-" + "m" * 36,
        document_name="chapter-guide.md",
        source_path="data/reference/chapter-guide.md",
        source_unit_count=9,
        chunk_count=14,
        indexed_point_count=14,
        status="failed",
        format="markdown",
        content_hash="markdown-hash-hf-r3",
        source_locator_scheme="markdown-heading-line-v1",
        error_message="request failed with API key=not-for-display",
    )

    pdf_markup = controller.document_inspector_markup("hf-r3-pdf-" + "p" * 36)
    markdown_markup = controller.document_inspector_markup("hf-r3-md-" + "m" * 36)

    assert 'class="docqa-document-inspector-card"' in pdf_markup
    assert "hf-r3-pdf-" + "p" * 36 in pdf_markup
    assert "pdf-hash-hf-r3" in pdf_markup
    assert "171 个定位单元 · 262 个分块 · 262 points" in pdf_markup
    assert "pdf-page-v1" in pdf_markup
    assert "MARKDOWN" in markdown_markup
    assert "markdown-heading-line-v1" in markdown_markup
    assert "not-for-display" not in markdown_markup
    assert "API key=[REDACTED]" in markdown_markup
    assert "选择一个文档查看详情" in _format_document_inspector({})
    controller.close()


def test_hf_r3_builds_controlled_library_toolbar_and_detail_selector(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "hf-r3-layout.sqlite3"))
    demo = build_app(controller)
    blocks = demo.blocks.values() if isinstance(demo.blocks, dict) else demo.blocks
    class_names = {
        class_name
        for block in blocks
        for class_name in (getattr(block, "elem_classes", None) or [])
    }

    assert {
        "docqa-library-search-field",
        "docqa-library-filter-bar",
        "docqa-document-inspector-markup",
        "docqa-detail-selector-controlled",
    } <= class_names
    assert "UI-REC1: single CSS authority" in APP_CSS
    assert "docqa-document-list-columns" in APP_CSS
    assert "docqa-inspector-metadata" in APP_CSS
    controller.close()


def test_ui_rec3_renders_selectable_rows_and_selected_document_metadata(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui-rec3-library.sqlite3"))
    controller.store.upsert_document(
        document_id="ui-rec3-pdf",
        document_name="REC3 产品手册.pdf",
        source_path="fixture/rec3.pdf",
        pages_with_text=18,
        chunk_count=32,
        indexed_point_count=32,
        status="indexed",
        content_hash="ui-rec3-pdf-hash",
        source_locator_scheme="pdf-page-v1",
    )
    controller.store.upsert_document(
        document_id="ui-rec3-markdown",
        document_name="REC3 学习指南.md",
        source_path="fixture/rec3.md",
        source_unit_count=6,
        chunk_count=9,
        indexed_point_count=9,
        status="archived",
        format="markdown",
        content_hash="ui-rec3-markdown-hash",
        source_locator_scheme="markdown-heading-line-v1",
    )

    markup = controller.document_library_markup(selected_document_id="ui-rec3-markdown")
    assert 'data-document-id="ui-rec3-pdf"' in markup
    assert 'data-document-id="ui-rec3-markdown"' in markup
    assert 'role="button"' in markup
    assert 'tabindex="0"' in markup
    assert 'class="docqa-document-row docqa-status-archived is-selected"' in markup
    assert 'aria-pressed="true"' in markup
    assert APP_JS.count("__docqaSelectedDocumentId") >= 1

    inspector = controller.document_inspector_markup("ui-rec3-markdown")
    assert "REC3 学习指南.md" in inspector
    assert "ui-rec3-markdown" in inspector
    assert "ui-rec3-markdown-hash" in inspector
    assert "MARKDOWN" in inspector
    assert "markdown-heading-line-v1" in inspector
    assert ".block.docqa-recent-title" in APP_CSS
    assert "margin-top: 12px" in APP_CSS
    assert ".block.docqa-recent-title .prose.docqa-recent-title" in APP_CSS
    assert ".docqa-upload-trigger > button .wrap" in APP_CSS
    assert "height: 42px" in APP_CSS
    controller.close()


def test_ui_hf3_builds_session_timeline_and_composer_contract(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui-hf3-layout.sqlite3"))
    demo = build_app(controller)
    blocks = demo.blocks.values() if isinstance(demo.blocks, dict) else demo.blocks
    class_names = {
        class_name
        for block in blocks
        for class_name in (getattr(block, "elem_classes", None) or [])
    }
    assert {"docqa-session-workspace", "docqa-timeline-panel", "docqa-composer"} <= class_names
    assert "docqa-chatbot" in APP_CSS
    assert "docqa-timeline-panel" in APP_CSS


def test_hf_r2_renders_real_history_as_timeline_without_fabricating_sources():
    markup = _format_session_timeline(
        [
            {"role": "user", "content": "What does <scope> mean?"},
            {
                "role": "assistant",
                "content": "It keeps the answer bounded.",
                "metadata": {"title": "2026-08-03T19:21:00"},
            },
        ],
        "✅ 回答完成",
        [{"citation_id": "source-1"}, {"citation_id": "source-2"}],
    )

    assert "docqa-timeline-user" in markup
    assert "docqa-timeline-assistant" in markup
    assert "&lt;scope&gt;" in markup
    assert "2 个来源" in markup
    assert "可保存为笔记" in markup
    assert "docqa-copy-answer" in markup
    assert "19:21" in markup
    assert "✅" not in markup

    empty_markup = _format_session_timeline([], "等待提问", {})
    assert "docqa-timeline-empty" in empty_markup
    assert "个来源" not in empty_markup


def test_hf_r2_builds_controlled_timeline_and_compact_composer_contract(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "hf-r2-layout.sqlite3"))
    demo = build_app(controller)
    blocks = demo.blocks.values() if isinstance(demo.blocks, dict) else demo.blocks
    class_names = {
        class_name
        for block in blocks
        for class_name in (getattr(block, "elem_classes", None) or [])
    }

    assert {"docqa-timeline-render", "docqa-composer-input", "docqa-composer-send"} <= class_names
    assert "docqa-timeline-empty" in APP_CSS
    assert "docqa-session-chip-row" in APP_CSS
    assert "docqa-composer-send" in APP_CSS
    controller.close()


def test_ui_rec2_keeps_scope_in_header_and_composer_as_one_surface(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui-rec2-layout.sqlite3"))
    demo = build_app(controller)
    blocks = demo.blocks.values() if isinstance(demo.blocks, dict) else demo.blocks
    class_names = {
        class_name
        for block in blocks
        for class_name in (getattr(block, "elem_classes", None) or [])
    }

    assert {
        "docqa-session-filter-chip",
        "docqa-composer-main",
        "docqa-composer-footer",
        "docqa-inspector-note-preview",
        "docqa-inspector-scope",
        "docqa-nav-library",
        "docqa-nav-session",
        "docqa-nav-context",
        "docqa-nav-reports",
    } <= class_names
    assert "docqa-session-scope" not in class_names
    assert "今天 · 学习记录" in _format_session_timeline([], "等待提问", {})
    assert "UI-REC2" not in APP_CSS
    assert "--docqa-shadow-panel: none" in APP_CSS
    assert "docqa-recent-item:first-child" in APP_CSS
    assert "docqa-inspector-section-title" in APP_CSS
    assert "来源与复习" in [getattr(block, "value", None) for block in blocks]
    controller.close()


def test_hf_r1_session_status_hides_internal_session_identifier(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "hf-r1.sqlite3"))

    session_id, status, *_ = controller.initialize()

    assert session_id.startswith("session_")
    assert status == "会话已就绪"
    assert session_id not in status
    assert "docqa-answer-status" in APP_CSS
    assert "docqa-composer" in APP_CSS
    controller.close()


def test_ui_hf4_renders_distinct_pdf_and_markdown_source_cards():
    markup = _format_source_cards([
        {
            "citation_id": "pdf-source",
            "document_name": "handbook.pdf",
            "page_start": 6,
            "page_end": 7,
            "source_locator": "handbook.pdf#page=6&chunk=c1",
            "score": 0.91,
            "content": "PDF source excerpt",
        },
        {
            "citation_id": "markdown-source",
            "document_name": "guide.md",
            "section": "Core chapter",
            "source_locator": "guide.md#section=Core%20chapter&paragraph=2&lines=11-14&chunk=c2",
            "score": 0.88,
            "content": "Markdown source excerpt",
        },
    ])

    assert markup.count('class="docqa-source-card"') == 2
    assert "docqa-source-badge-pdf" in markup
    assert "docqa-source-badge-markdown" in markup
    assert 'data-source-format="pdf"' in markup
    assert 'data-source-format="markdown"' in markup
    assert "展开片段和原始引用" in markup
    assert "第 6–7 页" in markup
    assert "Core chapter · 段落 2 · 行 11-14" in markup
    assert "handbook.pdf#page=6&amp;chunk=c1" in markup
    assert "guide.md#section=Core%20chapter" in markup


def test_ui_hf4_builds_context_inspector_card_contract(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui-hf4-layout.sqlite3"))
    demo = build_app(controller)
    blocks = demo.blocks.values() if isinstance(demo.blocks, dict) else demo.blocks
    class_names = {
        class_name
        for block in blocks
        for class_name in (getattr(block, "elem_classes", None) or [])
    }

    assert {
        "docqa-context-tabs",
        "docqa-note-editor",
        "docqa-notes-table",
        "docqa-note-list-markup",
        "docqa-sheet-handle",
        "docqa-context-close",
        "docqa-mobile-locator-note",
    } <= class_names
    assert "docqa-source-card" in APP_CSS
    assert "docqa-source-empty" in APP_CSS
    assert "docqa-note-status" in APP_CSS
    assert "docqa-mobile-context-toggle" in APP_CSS
    assert "height: min(390px, calc(100dvh - 96px))" in APP_CSS
    assert ".docqa-inspector:has(#document-inspector)" in APP_CSS
    assert "docqa-mobile-context-toggle input:checked" in APP_CSS
    assert "transform: translateY(105%)" in APP_CSS
    controller.close()


def test_ui_hfr4_formats_only_current_session_note_cards(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui-hfr4-notes.sqlite3"))
    session_id = controller.store.create_session().session_id
    other_session_id = controller.store.create_session().session_id
    first = controller.store.create_note(
        session_id=session_id,
        content="把来源拆成可复习的行动",
    )
    controller.store.create_note(
        session_id=other_session_id,
        content="不应出现在当前会话",
    )

    markup = controller.note_list_markup(session_id)

    assert first.note_id in markup
    assert "把来源拆成可复习的行动" in markup
    assert "当前会话" in markup
    assert "不应出现在当前会话" not in markup
    assert controller.note_list_markup(other_session_id).count('<article class="docqa-note-card"') == 1
    controller.close()


def test_ui_hf5_exposes_mobile_navigation_and_context_sheet_contract(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui-hf5-layout.sqlite3"))
    demo = build_app(controller)
    blocks = demo.blocks.values() if isinstance(demo.blocks, dict) else demo.blocks
    element_ids = {
        getattr(block, "elem_id", None)
        for block in blocks
        if getattr(block, "elem_id", None)
    }

    assert {"docqa-mobile-nav-toggle", "docqa-mobile-context-toggle", "sources-panel"} <= element_ids
    assert "UI-REC1: single CSS authority" in APP_CSS
    assert ":has(#docqa-mobile-nav-toggle input:checked)" in APP_CSS
    assert ":has(#docqa-mobile-context-toggle input:checked)" in APP_CSS
    assert "position: fixed" in APP_CSS
    assert "min-height: 44px" in APP_CSS
    controller.close()


def test_ui_hf5_lifecycle_actions_use_selected_document_detail_scope(tmp_path: Path):
    controller = UIController(Settings(sqlite_path=tmp_path / "ui-hf5-lifecycle-layout.sqlite3"))
    demo = build_app(controller)

    config = demo.get_config_file()
    components = {
        item["props"].get("label"): item["id"]
        for item in config.get("components", [])
        if item.get("props", {}).get("label")
    }
    detail_id = components["查看文档详情（不改变问答范围）"]
    scope_id = components["当前问答范围"]
    confirm_id = components["确认删除 Qdrant points；SQLite 历史保留"]
    lifecycle_inputs = {
        tuple(dependency.get("inputs", []))
        for dependency in config.get("dependencies", [])
        if len(dependency.get("outputs", [])) == 5
    }
    assert (detail_id,) in lifecycle_inputs
    assert (detail_id, confirm_id) in lifecycle_inputs
    assert (scope_id,) not in lifecycle_inputs
    controller.close()


def test_ui_rec1_owns_workbench_geometry_and_css_loading_contract():
    assert APP_CSS_PATH.name == "ui.css"
    assert APP_CSS_PATH.is_file()
    assert APP_CSS == APP_CSS_PATH.read_text(encoding="utf-8")
    assert "grid-template-columns: var(--docqa-sidebar-width) minmax(0, 1fr) var(--docqa-inspector-width)" in APP_CSS
    assert "grid-template-areas:" in APP_CSS
    assert '"sidebar main inspector"' in APP_CSS
    assert "footer," in APP_CSS
    assert ".docqa-composer" in APP_CSS
    assert APP_CSS.count("@media") == 3
    assert APP_CSS.count("!important") <= 162
    assert "UI-HF5" not in APP_CSS
    assert "HF-R3 owns" not in APP_CSS
