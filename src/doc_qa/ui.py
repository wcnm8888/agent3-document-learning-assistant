from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import gradio as gr

from .config import Settings
from .deepseek import DeepSeekChatProvider
from .document_catalog import DocumentCatalogService
from .document_scope import DocumentScopeState
from .embedding import DashScopeEmbeddingProvider
from .ingestion import DocumentIngestionService
from .learning import LearningService
from .lifecycle import DocumentLifecycleService
from .memory_store import SQLiteMemoryStore
from .models import IndexReport
from .qdrant_index import QdrantIndexer
from .qa import QuestionAnswerService


SUPPORTED_DOCUMENT_SUFFIXES = {".pdf", ".md", ".markdown"}

APP_CSS = """
:root {
  --docqa-ink: #17202a;
  --docqa-muted: #687482;
  --docqa-line: #e5e9ee;
  --docqa-surface: #ffffff;
  --docqa-soft: #f5f7f9;
  --docqa-accent: #2f6fed;
  --docqa-success: #16805c;
  --docqa-danger: #b42318;
  --docqa-warn: #9a6700;
}
body { background: #eef1f4 !important; color: var(--docqa-ink); }
#docqa-shell { max-width: 1480px; margin: 0 auto; padding: 18px; }
#docqa-shell .docqa-panel {
  background: var(--docqa-surface); border: 1px solid var(--docqa-line);
  border-radius: 8px; padding: 16px; box-shadow: 0 8px 24px rgba(23,32,42,.05);
}
#docqa-shell .docqa-title { margin: 0; color: var(--docqa-ink); }
#docqa-shell .docqa-kicker { color: var(--docqa-accent); font-size: 12px; letter-spacing: .08em; text-transform: uppercase; }
#docqa-shell .docqa-status { min-height: 42px; padding: 10px 12px; background: var(--docqa-soft); border-radius: 6px; }
#docqa-shell .docqa-scope { border-left: 3px solid var(--docqa-accent); }
#docqa-shell .gr-chatbot { min-height: 470px; }
#docqa-shell textarea, #docqa-shell input { font-size: 14px !important; }
#docqa-shell button { min-height: 40px; }
#docqa-shell .docqa-mobile-note { color: var(--docqa-muted); font-size: 12px; }
#docqa-shell .docqa-source-summary { font-size: 13px; line-height: 1.55; }
#docqa-shell .docqa-source-summary code { white-space: normal; overflow-wrap: anywhere; }
@media (max-width: 1100px) {
  #docqa-shell { padding: 12px; }
  #docqa-shell .docqa-panel { padding: 12px; }
  #docqa-shell .gr-chatbot { min-height: 390px; }
}
@media (max-width: 760px) {
  #docqa-shell { padding: 6px; }
  #docqa-shell .gr-row { flex-direction: column !important; }
  #docqa-shell .docqa-panel { width: 100% !important; }
  #docqa-shell .gr-chatbot { min-height: 330px; }
  #docqa-shell .docqa-source-panel { order: 3; }
  #docqa-shell .docqa-title { font-size: 22px; }
  #docqa-shell .docqa-mobile-note { margin-top: 4px; }
}
"""


def _safe_error(exc: Exception) -> str:
    message = str(exc).strip() or type(exc).__name__
    message = re.sub(r"Bearer\s+\S+", "Bearer [REDACTED]", message, flags=re.IGNORECASE)
    message = re.sub(r"(api[_-]?key\s*[=:]\s*)\S+", r"\1[REDACTED]", message, flags=re.IGNORECASE)
    message = re.sub(r"(token\s*[=:]\s*)\S+", r"\1[REDACTED]", message, flags=re.IGNORECASE)
    return f"{type(exc).__name__}: {message}"


def _safe_error_text(message: str | None) -> str:
    if not message:
        return ""
    return _safe_error(RuntimeError(message))


def _empty_stats() -> dict[str, Any]:
    return {
        "period_start": None,
        "period_end": None,
        "session_count": 0,
        "question_count": 0,
        "answered_count": 0,
        "no_results_count": 0,
        "note_count": 0,
        "document_count": 0,
        "daily_events": [],
    }


def _format_document_location(item: Any) -> str:
    if item.format == "markdown":
        return f"{item.source_unit_count} 个章节/段落单元"
    return f"{item.pages_with_text} 页"


def _short_document_id(document_id: str) -> str:
    return document_id if len(document_id) <= 16 else f"{document_id[:12]}…"


def _format_source_summary(citations: list[dict[str, Any]]) -> str:
    if not citations:
        return "暂无可展示的来源。"
    lines = ["**当前回答来源**"]
    for citation in citations:
        document_name = str(citation.get("document_name", "未知文档"))
        locator = str(citation.get("source_locator", "未知定位"))
        score = citation.get("score", "-")
        page_start = citation.get("page_start")
        page_end = citation.get("page_end")
        if page_start is not None:
            location = f"页码 {page_start}-{page_end}"
        else:
            location = "Markdown 章节/行号定位"
        lines.append(
            f"- **[{citation.get('citation_id', '?')}] {document_name}** · {location} · "
            f"相似度 `{score}` · `{locator}`"
        )
    return "\n".join(lines)


class UIController:
    """Gradio 适配层；文档、问答和学习数据仍由业务服务负责。"""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings.from_env()
        self.store = SQLiteMemoryStore(self.settings.sqlite_path)
        self._scope_state = DocumentScopeState()
        self._learning: LearningService | None = None
        self._ingestion: DocumentIngestionService | None = None
        self._learning_indexer: QdrantIndexer | None = None
        self._ingestion_indexer: QdrantIndexer | None = None
        self._lifecycle: DocumentLifecycleService | None = None

    def _ensure_learning(self) -> LearningService:
        if self._learning is not None:
            return self._learning
        embedding = DashScopeEmbeddingProvider(
            model_name=self.settings.embedding_model,
            expected_dimension=self.settings.embedding_dimension,
            api_key=self.settings.embedding_api_key,
            base_url=self.settings.embedding_base_url,
            batch_size=self.settings.embedding_batch_size,
            max_retries=self.settings.embedding_max_retries,
            retry_backoff_seconds=self.settings.embedding_retry_backoff_seconds,
        )
        indexer = QdrantIndexer(
            self.settings.collection_name,
            self.settings.embedding_dimension,
            url=self.settings.qdrant_url,
            api_key=self.settings.qdrant_api_key,
            local_path=self.settings.qdrant_local_path,
            timeout=self.settings.qdrant_timeout,
        )
        try:
            chat = DeepSeekChatProvider(
                api_key=self.settings.deepseek_api_key,
                base_url=self.settings.deepseek_base_url,
                model_name=self.settings.deepseek_model,
                thinking=self.settings.deepseek_thinking,
                trust_env=self.settings.deepseek_trust_env,
                max_retries=self.settings.deepseek_max_retries,
                retry_backoff_seconds=self.settings.deepseek_retry_backoff_seconds,
            )
        except Exception:
            indexer.close()
            raise
        qa = QuestionAnswerService(self.settings, query_embedding=embedding, chat=chat, indexer=indexer)
        self._learning_indexer = indexer
        self._learning = LearningService(self.settings, qa_service=qa, store=self.store)
        return self._learning

    def _ensure_ingestion(self) -> DocumentIngestionService:
        if self._ingestion is not None:
            return self._ingestion
        embedding = DashScopeEmbeddingProvider(
            model_name=self.settings.embedding_model,
            expected_dimension=self.settings.embedding_dimension,
            api_key=self.settings.embedding_api_key,
            base_url=self.settings.embedding_base_url,
            batch_size=self.settings.embedding_batch_size,
            max_retries=self.settings.embedding_max_retries,
            retry_backoff_seconds=self.settings.embedding_retry_backoff_seconds,
        )
        indexer = QdrantIndexer(
            self.settings.collection_name,
            self.settings.embedding_dimension,
            url=self.settings.qdrant_url,
            api_key=self.settings.qdrant_api_key,
            local_path=self.settings.qdrant_local_path,
            timeout=self.settings.qdrant_timeout,
        )
        self._ingestion_indexer = indexer
        self._ingestion = DocumentIngestionService(
            self.settings,
            embedding=embedding,
            indexer=indexer,
            catalog=DocumentCatalogService(self.store),
        )
        return self._ingestion

    def initialize(self) -> tuple[str, str, list[dict[str, str]], dict[str, Any], list[list[str]], dict[str, Any]]:
        session = self.store.create_session()
        self._scope_state = self._scope_state.all_documents()
        return (
            session.session_id,
            f"✅ 已创建学习会话 `{session.session_id}`",
            [],
            {},
            self.document_rows(),
            self.store.stats().as_dict(),
        )

    def document_rows(self) -> list[list[str]]:
        return self._document_rows_for(self.store.list_documents())

    def _document_rows_for(self, documents: list[Any]) -> list[list[str]]:
        return [
            [
                item.document_name,
                item.format.upper(),
                _short_document_id(item.document_id),
                item.status,
                _format_document_location(item),
                str(item.chunk_count),
                str(item.indexed_point_count),
                item.source_locator_scheme,
                item.updated_at,
                _safe_error_text(item.error_message),
            ]
            for item in documents
        ]

    def filter_documents(self, search: str | None, format_filter: str | None, status_filter: str | None, sort: str | None):
        documents = self.store.query_documents(
            search=search or "",
            format=None if not format_filter or format_filter == "全部格式" else format_filter.lower(),
            status=None if not status_filter or status_filter == "全部状态" else status_filter,
            sort=sort or "updated_desc",
        )
        return self._document_rows_for(documents)

    def document_details(self, document_id: str | None):
        if not document_id:
            return {}
        item = self.store.get_document(document_id)
        if item is None:
            return {"error": "文档不存在或已被移除"}
        return {
            "document_id": item.document_id,
            "document_name": item.document_name,
            "format": item.format,
            "status": item.status,
            "source_path": item.source_path,
            "content_hash": item.content_hash,
            "embedding": f"{item.embedding_model}/{item.embedding_dimension}",
            "source_locator_scheme": item.source_locator_scheme,
            "pages_or_units": item.pages_with_text if item.format == "pdf" else item.source_unit_count,
            "chunk_count": item.chunk_count,
            "indexed_point_count": item.indexed_point_count,
            "updated_at": item.updated_at,
            "error": _safe_error_text(item.error_message),
            "note": "PDF 使用页码定位；Markdown 使用章节/段落/行号定位。",
        }

    def _ensure_lifecycle(self) -> DocumentLifecycleService:
        if self._lifecycle is None:
            self._lifecycle = DocumentLifecycleService(
                self.store,
                QdrantIndexer(
                    self.settings.collection_name, self.settings.embedding_dimension,
                    url=self.settings.qdrant_url, api_key=self.settings.qdrant_api_key,
                    local_path=self.settings.qdrant_local_path, timeout=self.settings.qdrant_timeout,
                ),
            )
        return self._lifecycle

    def _lifecycle_result(self, action: str, document_id: str | None, confirm: bool = True):
        try:
            service = self._ensure_lifecycle()
            if action == "archive":
                record = service.archive(document_id or "")
                message = f"✅ 已归档：{record.document_name}（Qdrant points 保留）"
            elif action == "unarchive":
                record = service.unarchive(document_id or "")
                message = f"✅ 已取消归档：{record.document_name}"
            elif action == "delete":
                record = service.delete(document_id or "", confirm=confirm)
                message = f"✅ 已删除向量并保留 SQLite tombstone：{record.document_name}"
            else:
                record = service.restore_deleted(document_id or "", reindex=lambda source: self._ensure_ingestion().index_document(source))
                message = f"✅ 已重新索引恢复：{record.document_name}"
            return message, self.document_rows(), gr.update(choices=self.document_choices()), self.document_details(record.document_id)
        except Exception as exc:
            return f"❌ 生命周期操作失败：{_safe_error(exc)}", self.document_rows(), gr.update(choices=self.document_choices()), self.document_details(document_id)

    def document_choices(self) -> list[tuple[str, str]]:
        return [("全部文档", "")] + [
            (f"{item.document_name} · {item.format.upper()} · {item.status}", item.document_id)
            for item in self.store.list_documents()
        ]

    def refresh_document_choices(self):
        return gr.update(choices=self.document_choices())

    def _upsert_report_fallback(self, report: IndexReport, source: Path) -> None:
        if self.store.get_document(report.document_id) is not None:
            return
        self.store.upsert_document(
            document_id=report.document_id,
            document_name=report.document_name,
            source_path=report.source_path,
            pages_with_text=report.pages_with_text,
            chunk_count=report.chunk_count,
            indexed_point_count=report.indexed_point_count,
            status="indexed",
            format="markdown" if source.suffix.lower() in {".md", ".markdown"} else "pdf",
            content_hash=report.document_id,
            source_locator_scheme=(
                "markdown-heading-line-v1"
                if source.suffix.lower() in {".md", ".markdown"}
                else "pdf-page-v1"
            ),
            source_unit_count=report.pages_with_text,
        )

    def index_document(self, file_path: str | None):
        if not file_path:
            return "⚠️ 请先选择 PDF 或 Markdown 文件。", self.document_rows(), gr.update(choices=self.document_choices())
        source = Path(file_path)
        suffix = source.suffix.lower()
        if suffix not in SUPPORTED_DOCUMENT_SUFFIXES:
            return "❌ 仅支持 PDF、.md 和 .markdown 文件。", self.document_rows(), gr.update(choices=self.document_choices())
        if not source.is_file():
            return "❌ 文件不存在，请重新选择文件。", self.document_rows(), gr.update(choices=self.document_choices())
        try:
            if source.stat().st_size == 0:
                return "❌ 文件为空，无法建立索引。", self.document_rows(), gr.update(choices=self.document_choices())
            report = self._ensure_ingestion().index_document(source)
            self._upsert_report_fallback(report, source)
            status_text = "重复文档，未新增向量" if report.status == "duplicate" else "索引完成"
            message = (
                f"✅ {status_text}：{report.document_name} · {report.chunk_count} 个分块 · "
                f"{report.indexed_point_count} 个 points · {report.embedding_model}/{report.embedding_dimension}"
            )
            return message, self.document_rows(), gr.update(
                choices=self.document_choices(), value=report.document_id
            )
        except Exception as exc:
            return f"❌ 索引失败：{_safe_error(exc)}", self.document_rows(), gr.update(
                choices=self.document_choices()
            )

    def switch_document_scope(self, document_id: str | None):
        self._scope_state = self._scope_state.switch(document_id)
        label = document_id or "全部文档"
        return (
            f"已切换问答范围：`{label}`。当前回答、来源和临时上下文已清空，历史数据仍保留。",
            "等待提问",
            [],
            {},
            "暂无可展示的来源。",
            "",
            "",
            [],
            gr.update(choices=[], value=None),
            "",
        )

    def new_session(self):
        session = self.store.create_session()
        self._scope_state = self._scope_state.all_documents()
        return (
            session.session_id,
            f"✅ 已切换到新会话 `{session.session_id}`",
            [],
            {},
            "暂无可展示的来源。",
            "等待提问",
            "",
            "",
            [],
            gr.update(choices=[], value=None),
            "",
            self.store.stats().as_dict(),
        )

    def _append_context(self, question: str, answer: str) -> None:
        context = list(self._scope_state.conversation_context)
        context.append({"question": question, "answer": answer})
        while len(context) > self.settings.memory_turn_limit:
            context.pop(0)
        while sum(len(item.get("question", "")) + len(item.get("answer", "")) for item in context) > self.settings.memory_context_max_chars:
            if len(context) <= 1:
                break
            context.pop(0)
        self._scope_state = DocumentScopeState(
            document_id=self._scope_state.document_id,
            conversation_context=tuple(context),
            citations=self._scope_state.citations,
            pending_note=self._scope_state.pending_note,
        )

    def ask(
        self,
        session_id: str,
        question: str,
        document_id: str | None,
        chat_history: list[dict[str, str]] | None,
    ):
        if not session_id:
            session_id = self.store.create_session().session_id
        if not question or not question.strip():
            return (
                session_id, chat_history or [], "⚠️ 问题不能为空。", {}, "暂无可展示的来源。", "", "", [], gr.update(choices=[]), self.store.stats().as_dict()
            )
        self._scope_state = self._scope_state.switch(document_id)
        try:
            response = self._ensure_learning().ask(
                session_id,
                question.strip(),
                document_id=document_id or None,
                conversation_context=list(self._scope_state.conversation_context),
            )
            history = list(chat_history or [])
            history.extend([
                {"role": "user", "content": response.question},
                {"role": "assistant", "content": response.answer},
            ])
            turn = self.store.list_turns(session_id)[-1]
            citations = [citation.as_dict() for citation in response.citations]
            locator = response.citations[0].source_locator if response.citations else ""
            self._scope_state = DocumentScopeState(
                document_id=self._scope_state.document_id,
                conversation_context=self._scope_state.conversation_context,
                citations=tuple(citations),
                pending_note="",
            )
            if response.status == "answered":
                self._append_context(response.question, response.answer)
                status = "✅ 已回答"
            else:
                status = "ℹ️ 当前文档范围没有足够依据"
            note_choices = [(note.content[:42], note.note_id) for note in self.store.list_notes(session_id)]
            return (
                session_id,
                history,
                status,
                citations,
                _format_source_summary(citations),
                turn.turn_id,
                locator,
                self.note_rows(session_id),
                gr.update(choices=note_choices, value=None),
                self.store.stats().as_dict(),
            )
        except Exception as exc:
            return (
                session_id,
                chat_history or [],
                f"❌ 问答失败：{_safe_error(exc)}",
                {},
                "来源不可用。",
                "",
                "",
                self.note_rows(session_id),
                gr.update(choices=[]),
                self.store.stats().as_dict(),
            )

    def note_rows(self, session_id: str | None) -> list[list[str]]:
        return [
            [note.note_id, note.content, note.document_id or "", note.updated_at]
            for note in self.store.list_notes(session_id)
        ]

    def save_note(
        self,
        session_id: str,
        turn_id: str,
        document_id: str | None,
        source_locator: str,
        content: str,
    ):
        if not session_id or not turn_id:
            return "⚠️ 请先完成一次问答，再保存笔记。", [], gr.update(choices=[]), content
        try:
            note = self._ensure_learning().create_note(
                session_id,
                content,
                turn_id=turn_id,
                document_id=document_id or None,
                source_locator=source_locator or None,
            )
            choices = [(note.content[:42], note.note_id) for note in self.store.list_notes(session_id)]
            return f"✅ 笔记已保存：`{note.note_id}`", self.note_rows(session_id), gr.update(choices=choices, value=note.note_id), ""
        except Exception as exc:
            return f"❌ 笔记保存失败：{_safe_error(exc)}", self.note_rows(session_id), gr.update(choices=[]), content

    def load_note(self, note_id: str | None, session_id: str | None):
        if not note_id or not session_id:
            return ""
        for note in self.store.list_notes(session_id):
            if note.note_id == note_id:
                return note.content
        return ""

    def update_note(self, note_id: str, content: str, session_id: str):
        if not note_id:
            return "⚠️ 请先选择笔记。", self.note_rows(session_id)
        try:
            note = self._ensure_learning().update_note(note_id, content)
            return f"✅ 笔记已更新：`{note.note_id}`", self.note_rows(session_id)
        except Exception as exc:
            return f"❌ 笔记更新失败：{_safe_error(exc)}", self.note_rows(session_id)

    def refresh_stats(self, start_date: str | None, end_date: str | None):
        try:
            stats = self.store.stats(start_date or None, end_date or None).as_dict()
            return stats, self.store.report(start_date or None, end_date or None)
        except Exception as exc:
            return {"error": _safe_error(exc)}, {"error": _safe_error(exc)}

    def close(self) -> None:
        if self._learning_indexer:
            self._learning_indexer.close()
        if self._ingestion_indexer:
            self._ingestion_indexer.close()
        if self._lifecycle:
            self._lifecycle.indexer.close()
        self.store.close()


def build_app(controller: UIController | None = None) -> gr.Blocks:
    controller = controller or UIController()
    with gr.Blocks(title="文档学习助手", css=APP_CSS) as demo:
        session_state = gr.State("")
        current_turn_state = gr.State("")
        source_locator_state = gr.State("")

        with gr.Column(elem_id="docqa-shell"):
            gr.Markdown("# 文档学习助手", elem_classes=["docqa-title"])
            gr.Markdown("把阅读、提问和复习记录放在同一个工作台", elem_classes=["docqa-kicker"])
            with gr.Row():
                with gr.Column(scale=3, elem_classes=["docqa-panel"], elem_id="doc-library-panel"):
                    gr.Markdown("### 文档库")
                    document_status = gr.Markdown("等待上传 PDF 或 Markdown", elem_classes=["docqa-status"])
                    upload = gr.File(
                        label="上传 PDF 或 Markdown",
                        file_types=[".pdf", ".md", ".markdown"],
                        type="filepath",
                    )
                    index_button = gr.Button("开始索引", variant="primary")
                    document_table = gr.Dataframe(
                        headers=["文档", "格式", "document_id", "状态", "页数/单元", "分块", "points", "定位方式", "更新时间", "错误"],
                        datatype=["str"] * 10,
                        value=[],
                        interactive=False,
                        wrap=True,
                        label="已索引文档",
                    )
                    with gr.Row():
                        document_search = gr.Textbox(label="搜索文档", placeholder="文档名或 document_id")
                        document_format = gr.Dropdown(["全部格式", "PDF", "MARKDOWN"], value="全部格式", label="格式")
                        document_status_filter = gr.Dropdown(["全部状态", "indexed", "archived", "failed", "deleted", "inconsistent"], value="全部状态", label="状态")
                        document_sort = gr.Dropdown([("更新时间从新到旧", "updated_desc"), ("更新时间从旧到新", "updated_asc"), ("文档名升序", "name_asc")], value="updated_desc", label="排序")
                    document_detail = gr.JSON(label="文档详情", value={})
                    with gr.Row():
                        archive_button = gr.Button("归档")
                        unarchive_button = gr.Button("取消归档")
                        restore_button = gr.Button("重新索引恢复")
                    delete_confirm = gr.Checkbox(label="我确认删除该文档的 Qdrant points（SQLite 历史保留）", value=False)
                    delete_button = gr.Button("删除文档", variant="stop")
                    document_filter = gr.Dropdown(
                        choices=[("全部文档", "")], label="问答范围", value=""
                    )
                    scope_status = gr.Markdown("当前范围：全部文档", elem_classes=["docqa-status", "docqa-scope"])
                    gr.Markdown(
                        "支持 PDF 页码和 Markdown 章节/段落/行号定位；Markdown 不显示伪造页码。",
                        elem_classes=["docqa-mobile-note"],
                    )

                with gr.Column(scale=6, elem_classes=["docqa-panel"], elem_id="chat-panel"):
                    with gr.Row():
                        with gr.Column(scale=4):
                            gr.Markdown("### 学习会话")
                            session_status = gr.Markdown("正在初始化", elem_classes=["docqa-status"])
                        with gr.Column(scale=1):
                            new_session_button = gr.Button("新会话")
                    chatbot = gr.Chatbot(
                        label="问答记录",
                        type="messages",
                        placeholder="索引文档后，从一个问题开始。",
                    )
                    question = gr.Textbox(
                        label="向文档提问",
                        placeholder="例如：这份材料的核心章节如何推进？",
                        lines=3,
                    )
                    with gr.Row():
                        ask_button = gr.Button("提问", variant="primary")
                        clear_button = gr.Button("清空输入")
                    answer_status = gr.Markdown("等待提问", elem_classes=["docqa-status"])

                with gr.Column(scale=3, elem_classes=["docqa-panel", "docqa-source-panel"], elem_id="sources-panel"):
                    gr.Markdown("### 来源与复习")
                    sources = gr.JSON(label="来源引用（可展开查看片段）", value={})
                    source_summary = gr.Markdown("暂无可展示的来源。", elem_classes=["docqa-source-summary"])
                    note_content = gr.Textbox(label="学习笔记", lines=4, placeholder="记录你的理解、疑问或下一步行动")
                    save_note_button = gr.Button("保存为笔记", variant="primary")
                    note_status = gr.Markdown("等待保存笔记", elem_classes=["docqa-status"])
                    note_selector = gr.Dropdown(choices=[], label="选择已有笔记")
                    update_note_button = gr.Button("更新选中笔记")
                    notes_table = gr.Dataframe(
                        headers=["笔记 ID", "内容", "文档", "更新时间"],
                        datatype=["str"] * 4,
                        value=[],
                        interactive=False,
                        wrap=True,
                        label="笔记列表",
                    )

            with gr.Accordion("学习统计与报告", open=False):
                with gr.Row():
                    start_date = gr.Textbox(label="开始日期", placeholder="YYYY-MM-DD")
                    end_date = gr.Textbox(label="结束日期", placeholder="YYYY-MM-DD")
                    stats_button = gr.Button("刷新统计")
                stats_json = gr.JSON(label="统计", value=_empty_stats())
                report_json = gr.JSON(label="确定性报告", value={})

        clear_button.click(lambda: "", outputs=[question])
        demo.load(
            controller.initialize,
            outputs=[session_state, session_status, chatbot, sources, document_table, stats_json],
        )
        demo.load(controller.refresh_document_choices, outputs=[document_filter])
        for control in [document_search, document_format, document_status_filter, document_sort]:
            control.change(
                controller.filter_documents,
                inputs=[document_search, document_format, document_status_filter, document_sort],
                outputs=[document_table],
            )
        index_event = index_button.click(
            controller.index_document,
            inputs=[upload],
            outputs=[document_status, document_table, document_filter],
            show_progress="full",
        )
        index_event.then(
            controller.switch_document_scope,
            inputs=[document_filter],
            outputs=[scope_status, answer_status, chatbot, sources, source_summary, current_turn_state, source_locator_state, notes_table, note_selector, note_content],
        )
        document_filter.change(
            controller.switch_document_scope,
            inputs=[document_filter],
            outputs=[scope_status, answer_status, chatbot, sources, source_summary, current_turn_state, source_locator_state, notes_table, note_selector, note_content],
        )
        document_filter.change(controller.document_details, inputs=[document_filter], outputs=[document_detail])
        lifecycle_outputs = [document_status, document_table, document_filter, document_detail]
        archive_button.click(lambda document_id: controller._lifecycle_result("archive", document_id), inputs=[document_filter], outputs=lifecycle_outputs)
        unarchive_button.click(lambda document_id: controller._lifecycle_result("unarchive", document_id), inputs=[document_filter], outputs=lifecycle_outputs)
        restore_button.click(lambda document_id: controller._lifecycle_result("restore", document_id), inputs=[document_filter], outputs=lifecycle_outputs)
        delete_button.click(lambda document_id, confirm: controller._lifecycle_result("delete", document_id, confirm), inputs=[document_filter, delete_confirm], outputs=lifecycle_outputs)
        new_session_button.click(
            controller.new_session,
            outputs=[session_state, session_status, chatbot, sources, source_summary, answer_status, current_turn_state, source_locator_state, notes_table, note_selector, note_content, stats_json],
        )
        ask_outputs = [session_state, chatbot, answer_status, sources, source_summary, current_turn_state, source_locator_state, notes_table, note_selector, stats_json]
        ask_event = ask_button.click(
            controller.ask,
            inputs=[session_state, question, document_filter, chatbot],
            outputs=ask_outputs,
            show_progress="full",
        )
        question.submit(controller.ask, inputs=[session_state, question, document_filter, chatbot], outputs=ask_outputs, show_progress="full")
        ask_event.then(lambda: "", outputs=[question])
        save_note_button.click(
            controller.save_note,
            inputs=[session_state, current_turn_state, document_filter, source_locator_state, note_content],
            outputs=[note_status, notes_table, note_selector, note_content],
        )
        note_selector.change(controller.load_note, inputs=[note_selector, session_state], outputs=[note_content])
        update_note_button.click(
            controller.update_note,
            inputs=[note_selector, note_content, session_state],
            outputs=[note_status, notes_table],
        )
        stats_button.click(controller.refresh_stats, inputs=[start_date, end_date], outputs=[stats_json, report_json])
    return demo


def main() -> None:
    controller = UIController()
    demo = build_app(controller)
    try:
        demo.launch(
            server_name=os.getenv("GRADIO_SERVER_NAME", "127.0.0.1"),
            server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860")),
            share=False,
            show_error=True,
        )
    finally:
        controller.close()


if __name__ == "__main__":
    main()
