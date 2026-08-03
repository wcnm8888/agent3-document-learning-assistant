from __future__ import annotations

import os
import re
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

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

APP_CSS_PATH = Path(__file__).with_name("ui.css")


def _load_app_css() -> str:
    return APP_CSS_PATH.read_text(encoding="utf-8")


APP_CSS = _load_app_css()

APP_JS = r"""
() => {
  if (window.__docqaUiEventsBound) return;
  window.__docqaUiEventsBound = true;

  const copyText = async (text) => {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
  };

  document.addEventListener("click", (event) => {
    const row = event.target.closest(".docqa-document-row[data-document-id]");
    if (row) window.__docqaSelectedDocumentId = row.dataset.documentId;
  }, true);

  document.addEventListener("click", async (event) => {
    const button = event.target.closest(".docqa-copy-answer");
    if (!button) return;
    const answer = button.closest(".docqa-timeline-assistant")
      ?.querySelector(".docqa-timeline-content")?.innerText?.trim();
    if (!answer) return;
    try {
      await copyText(answer);
      button.dataset.state = "copied";
      button.setAttribute("aria-label", "回答已复制");
      window.setTimeout(() => {
        button.dataset.state = "idle";
        button.setAttribute("aria-label", "复制回答");
      }, 1400);
    } catch (error) {
      button.dataset.state = "failed";
      window.setTimeout(() => { button.dataset.state = "idle"; }, 1400);
    }
  });

  document.addEventListener("keydown", (event) => {
    const documentRow = event.target.closest(".docqa-document-row[data-document-label]");
    if (!documentRow || !["Enter", " "].includes(event.key)) return;
    event.preventDefault();
    documentRow.click();
  });
}
"""


def _format_turn_time(value: Any) -> tuple[str, str]:
    """Return an escaped ISO value and local HH:MM label for real turn timestamps."""
    raw_value = str(value or "").strip()
    if not raw_value:
        return "", ""
    try:
        parsed = datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone()
        return escape(raw_value), parsed.strftime("%H:%M")
    except ValueError:
        return escape(raw_value), ""

def _safe_error(exc: Exception) -> str:
    message = str(exc).strip() or type(exc).__name__
    message = re.sub(r"Bearer\s+\S+", "Bearer [REDACTED]", message, flags=re.IGNORECASE)
    message = re.sub(r"(api[\s_-]?key\s*[=:]\s*)\S+", r"\1[REDACTED]", message, flags=re.IGNORECASE)
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


def _format_document_updated_at(value: Any) -> tuple[str, str]:
    """Return the real timestamp and a compact library-row label."""
    raw_value = str(value or "").strip()
    if not raw_value:
        return "未记录", "未记录"
    try:
        parsed = datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone()
        return raw_value, parsed.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return raw_value, raw_value


def _format_source_summary(citations: list[dict[str, Any]]) -> str:
    if not citations:
        return "暂无可展示的来源。"
    lines = ["**当前回答来源**", "", "回答中的每个来源都保留原文定位；点击右侧原始数据可查看完整字段。"]
    for citation in citations:
        document_name = escape(str(citation.get("document_name", "未知文档")))
        locator = escape(str(citation.get("source_locator", "未知定位")))
        section = escape(str(citation.get("section", "") or ""))
        score = citation.get("score", "-")
        page_start = citation.get("page_start")
        page_end = citation.get("page_end")
        if page_start is not None:
            page_end = page_end or page_start
            location = f"PDF · 第 {page_start}–{page_end} 页"
        else:
            parsed_locator = urlparse(str(citation.get("source_locator", "")))
            query = parse_qs(parsed_locator.query or parsed_locator.fragment)
            paragraph = query.get("paragraph", [""])[0]
            line_range = query.get("lines", [""])[0]
            location_parts = ["Markdown"]
            if section:
                location_parts.append(section)
            if paragraph:
                location_parts.append(f"段落 {escape(paragraph)}")
            if line_range:
                location_parts.append(f"行 {escape(line_range)}")
            location = " · ".join(location_parts)
        content = escape(str(citation.get("content", "") or "").strip())
        excerpt = content[:240] + ("…" if len(content) > 240 else "")
        lines.append(
            f"\n### [{escape(str(citation.get('citation_id', '?')))}] {document_name}\n"
            f"`{location}` · 相似度 `{escape(str(score))}`\n\n"
            f"> {excerpt.replace(chr(10), '<br>')}\n\n"
            f"定位：`{locator}`"
        )
    return "\n".join(lines)


def _format_source_cards(citations: list[dict[str, Any]]) -> str:
    """Render citations as semantic inspector cards without changing citation data."""
    if not citations:
        return (
            '<div class="docqa-source-empty">'
            '<strong>暂无可展示的来源</strong>'
            '<span>完成一次问答后，PDF 页码或 Markdown 章节定位会显示在这里。</span>'
            '</div>'
        )

    cards: list[str] = []
    for citation in citations:
        locator_raw = str(citation.get("source_locator", "未知定位"))
        parsed_locator = urlparse(locator_raw)
        query = parse_qs(parsed_locator.query or parsed_locator.fragment)
        page_start = citation.get("page_start")
        page_end = citation.get("page_end") or page_start
        is_pdf = page_start is not None or parsed_locator.path.lower().endswith(".pdf")

        if is_pdf:
            location = f"第 {page_start or '-'} 页"
            if page_end and page_end != page_start:
                location = f"第 {page_start}–{page_end} 页"
            badge_class = "docqa-source-badge-pdf"
            format_label = "PDF"
        else:
            section = str(citation.get("section", "") or query.get("section", [""])[0])
            paragraph = query.get("paragraph", [""])[0]
            line_range = query.get("lines", [""])[0]
            location_parts = [part for part in [section, f"段落 {paragraph}" if paragraph else "", f"行 {line_range}" if line_range else ""] if part]
            location = " · ".join(location_parts) or "Markdown 原文定位"
            badge_class = "docqa-source-badge-markdown"
            format_label = "MARKDOWN"

        excerpt_text = str(citation.get("content", "") or "").strip()
        if len(excerpt_text) > 240:
            excerpt_text = excerpt_text[:240] + "…"
        document_name = escape(str(citation.get("document_name", "未知文档")))
        citation_id = escape(str(citation.get("citation_id", "来源")))
        score = escape(str(citation.get("score", "-")))
        location = escape(location)
        locator = escape(locator_raw)
        excerpt = escape(excerpt_text).replace("\n", "<br>")
        cards.append(
            f'<article class="docqa-source-card" data-citation-id="{citation_id}" '
            f'data-source-format="{format_label.lower()}">'
            '<div class="docqa-source-card-head">'
            f'<span class="docqa-source-badge {badge_class}">{format_label}</span>'
            f'<span class="docqa-source-score">相似度 {score}</span>'
            '</div>'
            '<div class="docqa-source-card-primary">'
            f'<span class="docqa-source-card-name">{document_name}</span>'
            f'<span class="docqa-source-location">{location}</span>'
            '</div>'
            '<details class="docqa-source-expand">'
            '<summary>展开片段和原始引用 <span aria-hidden="true">›</span></summary>'
            f'<p class="docqa-source-excerpt">{excerpt or "暂无来源片段"}</p>'
            f'<p class="docqa-source-locator">原始定位：<code>{locator}</code></p>'
            '</details>'
            '</article>'
        )
    return '<section class="docqa-source-cards" aria-label="回答来源">' + "".join(cards) + "</section>"


def _format_note_cards(notes: list[Any]) -> str:
    """Render the current session's real notes as compact inspector cards."""
    if not notes:
        return (
            '<section class="docqa-note-cards docqa-note-empty" aria-label="学习笔记列表">'
            '<strong>暂无学习笔记</strong>'
            '<span>完成问答后，可将当前理解保存为下一次复习的行动。</span>'
            '</section>'
        )

    cards: list[str] = []
    for note in notes:
        note_id = escape(str(getattr(note, "note_id", "笔记")))
        document_id = escape(str(getattr(note, "document_id", "") or "当前会话"))
        updated_at = escape(str(getattr(note, "updated_at", "未记录")))
        content_text = str(getattr(note, "content", "") or "").strip()
        if len(content_text) > 140:
            content_text = content_text[:140] + "…"
        content = escape(content_text).replace("\n", "<br>")
        cards.append(
            f'<article class="docqa-note-card" data-note-id="{note_id}">'
            '<div class="docqa-note-card-head">'
            '<span class="docqa-note-card-label">学习笔记</span>'
            f'<time>{updated_at}</time>'
            '</div>'
            f'<p class="docqa-note-card-content">{content or "（空笔记）"}</p>'
            '<div class="docqa-note-card-meta">'
            f'<span>文档 <code>{document_id}</code></span>'
            f'<span>笔记 <code>{note_id}</code></span>'
            '</div>'
            '</article>'
        )
    return '<section class="docqa-note-cards" aria-label="学习笔记列表">' + "".join(cards) + "</section>"


def _format_session_timeline(
    history: list[dict[str, Any]] | None,
    status: str = "等待提问",
    citations: list[dict[str, Any]] | dict[str, Any] | None = None,
) -> str:
    """Render real Chatbot history as the Figma-aligned session presentation layer."""
    safe_history = history if isinstance(history, list) else []
    safe_citations = citations if isinstance(citations, list) else []
    normalized_status = re.sub(r"^[✅✔☑]\s*", "", str(status or "等待提问")).strip()
    safe_status = escape(normalized_status)

    if not safe_history:
        return (
            '<section class="docqa-timeline" aria-live="polite">'
            '<div class="docqa-timeline-separator">今天 · 学习记录</div>'
            '<div class="docqa-timeline-empty">'
            '<strong>从一个问题开始</strong>'
            '<span>回答、来源和可保存笔记会显示在这里。</span>'
            '</div>'
            f'<div class="docqa-timeline-state">{safe_status}</div>'
            '</section>'
        )

    message_markup: list[str] = ['<section class="docqa-timeline" aria-live="polite">']
    message_markup.append('<div class="docqa-timeline-separator">今天 · 学习记录</div>')
    last_index = len(safe_history) - 1
    for index, message in enumerate(safe_history):
        role = str(message.get("role", "assistant"))
        content = escape(str(message.get("content", "") or "")).replace("\n", "<br>")
        if role == "user":
            message_markup.append(
                '<article class="docqa-timeline-message docqa-timeline-user">'
                '<span class="docqa-timeline-role">问题</span>'
                f'<div class="docqa-timeline-content">{content}</div>'
                '</article>'
            )
            continue

        metadata = ""
        if index == last_index and safe_citations:
            source_count = len(safe_citations)
            metadata = (
                '<div class="docqa-timeline-meta">'
                f'<span>{source_count} 个来源</span>'
                '<span>可保存为笔记</span>'
                '</div>'
            )
        message_markup.append(
            '<article class="docqa-timeline-message docqa-timeline-assistant">'
            '<span class="docqa-timeline-role">回答</span>'
            f'<div class="docqa-timeline-content">{content}</div>'
            f'{metadata}'
            '<div class="docqa-answer-tools">'
            '<button class="docqa-copy-answer" type="button" data-state="idle" '
            'aria-label="复制回答" title="复制回答"><span aria-hidden="true"></span></button>'
            f'{_format_answer_time(message)}'
            '</div>'
            '</article>'
        )
    if normalized_status not in {"已回答", "回答完成"}:
        message_markup.append(f'<div class="docqa-timeline-state">{safe_status}</div>')
    message_markup.append('</section>')
    return "".join(message_markup)


def _format_answer_time(message: dict[str, Any]) -> str:
    metadata = message.get("metadata") if isinstance(message, dict) else None
    timestamp = metadata.get("title") if isinstance(metadata, dict) else ""
    iso_value, label = _format_turn_time(timestamp)
    if not label:
        return ""
    return f'<time class="docqa-answer-time" datetime="{iso_value}">{label}</time>'


def _format_document_detail_summary(detail: dict[str, Any]) -> str:
    if not detail:
        return "选择文档后，这里会显示完整 ID、格式、状态、定位规则和索引统计。"
    if detail.get("error") and not detail.get("document_id"):
        return f"**无法加载文档详情**\n\n`{escape(str(detail['error']))}`"
    document_name = escape(str(detail.get("document_name", "未命名文档")))
    document_id = escape(str(detail.get("document_id", "")))
    document_format = escape(str(detail.get("format", "unknown")).upper())
    status = escape(_document_status_label(str(detail.get("status", "unknown"))))
    content_hash = escape(str(detail.get("content_hash") or "未记录"))
    locator_scheme = escape(str(detail.get("source_locator_scheme") or "未记录"))
    location_units = escape(str(detail.get("pages_or_units") or 0))
    chunk_count = escape(str(detail.get("chunk_count") or 0))
    point_count = escape(str(detail.get("indexed_point_count") or 0))
    updated_at = escape(str(detail.get("updated_at") or "未记录"))
    error = escape(str(detail.get("error") or ""))
    location = escape(str(detail.get("note", "")))
    error_block = (
        f"\n\n**错误详情**\n\n<div class=\"docqa-detail-error\">{error}</div>"
        if error else ""
    )
    return (
        f"### {document_name}\n"
        f"<span class=\"docqa-detail-badge\">{document_format}</span> "
        f"<span class=\"docqa-detail-status\">{status}</span>\n\n"
        f"**document_id**\n`{document_id}`\n\n"
        f"**内容 hash**\n`{content_hash}`\n\n"
        f"**索引统计**\n\n"
        f"- 定位单元：`{location_units}`\n"
        f"- 分块：`{chunk_count}`\n"
        f"- Qdrant points：`{point_count}`\n"
        f"- 更新时间：`{updated_at}`\n\n"
        f"**定位方案**\n`{locator_scheme}`\n\n"
        f"{location}{error_block}"
    )


def _format_document_inspector(detail: dict[str, Any]) -> str:
    """Render the document-library inspector from real catalog metadata only."""
    if not detail:
        return (
            '<section class="docqa-inspector-empty">'
            '<strong>选择一个文档查看详情</strong>'
            '<span>完整 document_id、hash、索引统计和生命周期入口会显示在这里。</span>'
            '</section>'
        )
    if detail.get("error") and not detail.get("document_id"):
        return (
            '<section class="docqa-inspector-empty docqa-inspector-error">'
            '<strong>无法加载文档详情</strong>'
            f'<span>{escape(str(detail["error"]))}</span>'
            '</section>'
        )

    document_name = escape(str(detail.get("document_name", "未命名文档")))
    document_id = escape(str(detail.get("document_id", "未记录")))
    document_format = escape(str(detail.get("format", "unknown")).upper())
    status = str(detail.get("status", "unknown"))
    status_label = escape(_document_status_label(status))
    content_hash = escape(str(detail.get("content_hash") or "未记录"))
    locator_scheme = escape(str(detail.get("source_locator_scheme") or "未记录"))
    location_units = escape(str(detail.get("pages_or_units") or 0))
    chunk_count = escape(str(detail.get("chunk_count") or 0))
    point_count = escape(str(detail.get("indexed_point_count") or 0))
    updated_at = escape(str(detail.get("updated_at") or "未记录"))
    location_note = escape(str(detail.get("note") or ""))
    error = escape(str(detail.get("error") or ""))
    error_block = (
        '<div class="docqa-inspector-error-detail">'
        '<span>索引错误详情</span>'
        f'<p>{error}</p>'
        '</div>'
        if error
        else ""
    )
    return (
        '<section class="docqa-document-inspector-card">'
        '<span class="docqa-inspector-eyebrow">文档详情</span>'
        f'<h2 title="{document_name}">{document_name}</h2>'
        '<div class="docqa-inspector-badges">'
        f'<span class="docqa-detail-status docqa-detail-status-{escape(status)}">{status_label}</span>'
        '</div>'
        '<dl class="docqa-inspector-metadata">'
        '<div><dt>格式</dt>'
        f'<dd>{document_format}</dd></div>'
        '<div><dt>document_id</dt>'
        f'<dd><code>{document_id}</code></dd></div>'
        '<div><dt>文件 hash</dt>'
        f'<dd><code>{content_hash}</code></dd></div>'
        '<div><dt>索引统计</dt>'
        f'<dd>{location_units} 个定位单元 · {chunk_count} 个分块 · {point_count} points</dd></div>'
        '<div><dt>来源定位</dt>'
        f'<dd>{locator_scheme}</dd></div>'
        '<div><dt>更新时间</dt>'
        f'<dd>{updated_at}</dd></div>'
        '</dl>'
        f'<p class="docqa-inspector-location-note">{location_note}</p>'
        f'{error_block}'
        '</section>'
    )

_DOCUMENT_STATUS_LABELS = {
    "indexed": "已索引",
    "archived": "已归档",
    "failed": "索引失败",
    "deleted": "已删除",
    "inconsistent": "需校验",
    "pending": "待处理",
    "validating": "校验中",
    "parsing": "解析中",
    "indexing": "索引中",
}


def _document_status_label(status: str) -> str:
    return _DOCUMENT_STATUS_LABELS.get(status, status or "未知状态")


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
            "会话已就绪",
            [],
            {},
            self.document_table_rows(),
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

    def _document_table_rows_for(self, documents: list[Any]) -> list[list[str]]:
        """Return the compact UI view; full metadata remains available in details."""
        return [
            [
                item.document_name,
                item.format.upper(),
                item.status,
                item.updated_at,
            ]
            for item in documents
        ]

    def document_table_rows(self) -> list[list[str]]:
        return self._document_table_rows_for(self.store.list_documents())

    def recent_document_rows(self, limit: int = 5) -> list[list[str]]:
        """Return the sidebar snapshot without changing the document catalog semantics."""
        return [
            [item.document_name, f"{item.format.upper()} · {item.status}"]
            for item in self.store.list_documents()[:limit]
        ]

    def recent_document_markup(self, limit: int = 5) -> str:
        """Render the real recent-document snapshot as a UI-only navigation list."""
        items = self.store.list_documents()[:limit]
        if not items:
            return '<div class="docqa-recent-empty">暂无最近文档。上传并索引文档后，会显示在这里。</div>'
        rows = []
        for item in items:
            name = escape(item.document_name)
            metadata = escape(f"{item.format.upper()} · {item.status}")
            rows.append(
                f'<div class="docqa-recent-item"><span class="docqa-recent-name">{name}</span>'
                f'<span class="docqa-recent-meta">{metadata}</span></div>'
            )
        return f'<div class="docqa-recent-list">{"".join(rows)}</div>'

    @staticmethod
    def _document_query_values(
        format_filter: str | None,
        status_filter: str | None,
        sort: str | None,
    ) -> tuple[str | None, str | None, str]:
        return (
            None if not format_filter or format_filter == "全部格式" else format_filter.lower(),
            None if not status_filter or status_filter == "全部状态" else status_filter,
            sort or "updated_desc",
        )

    def _filtered_documents(
        self,
        search: str | None,
        format_filter: str | None,
        status_filter: str | None,
        sort: str | None,
    ) -> list[Any]:
        document_format, document_status, document_sort = self._document_query_values(
            format_filter, status_filter, sort
        )
        return self.store.query_documents(
            search=search or "",
            format=document_format,
            status=document_status,
            sort=document_sort,
        )

    def document_library_markup(
        self,
        search: str | None = "",
        format_filter: str | None = "全部格式",
        status_filter: str | None = "全部状态",
        sort: str | None = "updated_desc",
        selected_document_id: str | None = None,
    ) -> str:
        """Render selectable document rows without changing document-query semantics."""
        documents = self._filtered_documents(search, format_filter, status_filter, sort)
        if not documents:
            return (
                '<div class="docqa-library-empty">'
                '<strong>没有匹配的文档</strong>'
                '<span>调整搜索或筛选条件，或上传并索引一份 PDF / Markdown。</span>'
                '</div>'
            )
        rows: list[str] = [
            '<div class="docqa-document-list-columns">'
            '<span>文档</span><span>格式</span><span>状态</span><span>更新时间</span>'
            '</div>'
        ]
        selected_id = selected_document_id or str(documents[0].document_id)
        for item in documents:
            name = escape(str(item.document_name))
            document_id = escape(str(item.document_id))
            document_label = escape(
                f"{item.document_name} · {str(item.format).upper()} · {item.status}"
            )
            document_format = escape(str(item.format).upper())
            status = str(item.status or "unknown")
            status_label = escape(_document_status_label(status))
            updated_at_raw, updated_at_label = _format_document_updated_at(item.updated_at)
            updated_at = escape(updated_at_raw)
            updated_label = escape(updated_at_label)
            location = escape(_format_document_location(item))
            chunks = escape(str(item.chunk_count or 0))
            selected = str(item.document_id) == selected_id
            selected_class = " is-selected" if selected else ""
            selected_state = "true" if selected else "false"
            error_hint = ""
            if item.error_message:
                error_hint = f'<span class="docqa-document-error">{escape(_safe_error_text(item.error_message))}</span>'
            rows.append(
                f'<article class="docqa-document-row docqa-status-{escape(status)}{selected_class}" '
                f'data-document-id="{document_id}" data-document-label="{document_label}" '
                f'role="button" tabindex="0" aria-pressed="{selected_state}">'
                f'<div class="docqa-document-main">'
                f'<strong class="docqa-document-name" title="{name}">{name}</strong>'
                f'<span class="docqa-document-meta">{location} · {chunks} 个分块{error_hint}</span>'
                f'</div>'
                f'<span class="docqa-document-format">{document_format}</span>'
                f'<span class="docqa-document-status docqa-status-pill">{status_label}</span>'
                f'<time class="docqa-document-time" title="{updated_at}">{updated_label}</time>'
                f'</article>'
            )
        return f'<div class="docqa-document-list">{"".join(rows)}</div>'

    def document_library_count(
        self,
        search: str | None = "",
        format_filter: str | None = "全部格式",
        status_filter: str | None = "全部状态",
        sort: str | None = "updated_desc",
    ) -> str:
        count = len(self._filtered_documents(search, format_filter, status_filter, sort))
        return f"{count} 个文档"

    def filter_documents(self, search: str | None, format_filter: str | None, status_filter: str | None, sort: str | None):
        documents = self._filtered_documents(search, format_filter, status_filter, sort)
        return self._document_rows_for(documents)

    def filter_document_table_rows(
        self, search: str | None, format_filter: str | None, status_filter: str | None, sort: str | None
    ):
        documents = self._filtered_documents(search, format_filter, status_filter, sort)
        return self._document_table_rows_for(documents)

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

    def document_detail_summary(self, document_id: str | None) -> str:
        return _format_document_detail_summary(self.document_details(document_id))

    def document_inspector_markup(self, document_id: str | None) -> str:
        return _format_document_inspector(self.document_details(document_id))

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

    def _lifecycle_table_result(self, action: str, document_id: str | None, confirm: bool = True):
        result = self._lifecycle_result(action, document_id, confirm)
        return result[0], self.document_table_rows(), result[2], result[3], _format_document_detail_summary(result[3])

    def document_choices(self) -> list[tuple[str, str]]:
        return [("全部文档", "")] + [
            (f"{item.document_name} · {item.format.upper()} · {item.status}", item.document_id)
            for item in self.store.list_documents()
        ]

    def refresh_document_choices(self):
        return gr.update(choices=self.document_choices())

    def default_document_detail_id(self) -> str:
        documents = self.store.list_documents()
        return documents[0].document_id if documents else ""

    def refresh_document_detail_selector(self):
        return gr.update(
            choices=self.document_choices(),
            value=self.default_document_detail_id(),
        )

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

    def index_document_table(self, file_path: str | None):
        result = self.index_document(file_path)
        return result[0], self.document_table_rows(), result[2]

    def switch_document_scope(self, document_id: str | None):
        self._scope_state = self._scope_state.switch(document_id)
        label = document_id or "全部文档"
        return (
            f"已切换问答范围：`{label}`。当前回答、来源和临时上下文已清空，历史数据仍保留。",
            "等待提问",
            [],
            {},
            _format_source_cards([]),
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
            "✅ 已切换到新会话",
            [],
            {},
            _format_source_cards([]),
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
                session_id, chat_history or [], "⚠️ 问题不能为空。", {}, _format_source_cards([]), "", "", [], gr.update(choices=[]), self.store.stats().as_dict()
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
            history[-1]["metadata"] = {"title": turn.created_at}
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
                status = "已回答"
            else:
                status = "ℹ️ 当前文档范围没有足够依据"
            note_choices = [(note.content[:42], note.note_id) for note in self.store.list_notes(session_id)]
            return (
                session_id,
                history,
                status,
                citations,
                _format_source_cards(citations),
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
                _format_source_cards([]),
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

    def note_list_markup(self, session_id: str | None) -> str:
        """Presentation-only note cards; storage and session isolation stay in the store."""
        return _format_note_cards(self.store.list_notes(session_id))

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
    initial_document_detail_id = controller.default_document_detail_id()

    def show_library():
        return (
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(variant="primary"),
            gr.update(variant="secondary"),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(value=False),
            gr.update(value=False),
            gr.update(value="文档详情"),
            gr.update(value="完整标识、索引统计、错误详情和生命周期操作"),
            gr.update(visible=False),
        )

    def show_session():
        return (
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(variant="secondary"),
            gr.update(variant="primary"),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(value=False),
            gr.update(value=False),
            gr.update(value="来源与复习"),
            gr.update(value="回答中的证据按文档类型显示定位方式。"),
            gr.update(visible=False),
        )

    def show_context():
        """Open the session workspace and its mobile context sheet."""
        return (
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(variant="secondary"),
            gr.update(variant="primary"),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(value=False),
            gr.update(value=True),
            gr.update(value="来源与复习"),
            gr.update(value="回答中的证据按文档类型显示定位方式。"),
            gr.update(visible=False),
        )

    def show_reports():
        return (
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(variant="secondary"),
            gr.update(variant="secondary"),
            gr.update(open=True, visible=True),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(value=False),
            gr.update(value=False),
            gr.update(value="学习统计与报告"),
            gr.update(value="查看学习活动统计和确定性报告。"),
        )

    def initial_view():
        has_documents = bool(controller.store.list_documents())
        return (
            gr.update(visible=not has_documents),
            gr.update(visible=has_documents),
            gr.update(variant="primary" if not has_documents else "secondary"),
            gr.update(variant="primary" if has_documents else "secondary"),
            gr.update(visible=has_documents),
            gr.update(visible=not has_documents),
            gr.update(value=False),
            gr.update(value=False),
            gr.update(value="来源与复习" if has_documents else "文档详情"),
            gr.update(
                value=(
                    "回答中的证据按文档类型显示定位方式。"
                    if has_documents
                    else "完整标识、索引统计、错误详情和生命周期操作"
                )
            ),
            gr.update(visible=False),
        )

    def mirror_rows(rows):
        return rows

    def select_document_detail(document_id: str | None):
        selected_id = document_id or controller.default_document_detail_id()
        return (
            gr.update(value=selected_id),
            controller.document_details(selected_id),
            controller.document_detail_summary(selected_id),
            controller.document_inspector_markup(selected_id),
        )

    with gr.Blocks(title="文档学习助手", css=APP_CSS, js=APP_JS) as demo:
        session_state = gr.State("")
        current_turn_state = gr.State("")
        source_locator_state = gr.State("")

        with gr.Column(elem_id="docqa-shell"):
            with gr.Row(elem_classes=["docqa-topbar"]):
                with gr.Row(elem_classes=["docqa-brand"], scale=5):
                    gr.Markdown("▦", elem_classes=["docqa-brand-mark"])
                    with gr.Column(elem_classes=["docqa-brand-copy"]):
                        gr.Markdown("文档学习助手", elem_classes=["docqa-title"])
                        gr.Markdown("阅读 · 提问 · 复习", elem_classes=["docqa-kicker"])
                with gr.Row(elem_classes=["docqa-topbar-meta"], scale=4):
                    topbar_scope = gr.Markdown("全部文档", elem_classes=["docqa-topbar-chip", "docqa-topbar-scope"])
                    gr.Markdown("本地运行", elem_classes=["docqa-topbar-chip", "docqa-topbar-runtime"])
                    gr.Markdown("文", elem_classes=["docqa-topbar-chip", "docqa-topbar-language"])

            with gr.Row(elem_classes=["docqa-mobile-actions"], scale=0):
                mobile_nav_toggle = gr.Checkbox(
                    label="菜单",
                    value=False,
                    interactive=True,
                    elem_id="docqa-mobile-nav-toggle",
                    elem_classes=["docqa-mobile-nav-toggle"],
                )
                mobile_context_toggle = gr.Checkbox(
                    label="来源与笔记",
                    value=False,
                    interactive=True,
                    elem_id="docqa-mobile-context-toggle",
                    elem_classes=["docqa-mobile-context-toggle"],
                )

            with gr.Row(elem_id="docqa-workspace", elem_classes=["docqa-workspace"]):
                with gr.Column(scale=0, min_width=220, elem_classes=["docqa-sidebar"], elem_id="docqa-sidebar"):
                    gr.Markdown("空间", elem_classes=["docqa-section-kicker"])
                    with gr.Column(elem_classes=["docqa-space-nav"]):
                        nav_library_button = gr.Button("文档库", variant="secondary", elem_classes=["docqa-nav-item", "docqa-nav-library"])
                        nav_session_button = gr.Button("学习会话", variant="secondary", elem_classes=["docqa-nav-item", "docqa-nav-session"])
                        nav_context_button = gr.Button("来源与笔记", variant="secondary", elem_classes=["docqa-nav-item", "docqa-nav-context"])
                        nav_reports_button = gr.Button("学习报告", variant="secondary", elem_classes=["docqa-nav-item", "docqa-nav-reports"])
                    gr.Markdown("最近文档", elem_classes=["docqa-recent-title"])
                    recent_documents = gr.HTML(
                        value=controller.recent_document_markup(),
                        elem_classes=["docqa-recent-block"],
                    )
                    gr.Markdown(
                        "<strong>本地知识工作台</strong><br>PDF / Markdown · 单用户",
                        elem_classes=["docqa-sidebar-footer"],
                    )

                with gr.Column(scale=1, elem_classes=["docqa-main-region"]):
                    with gr.Group(visible=False, elem_id="library-view", elem_classes=["docqa-library-view"]) as library_view:
                        with gr.Row(elem_classes=["docqa-library-header"]):
                            with gr.Column(scale=5):
                                gr.Markdown("知识库", elem_classes=["docqa-eyebrow"])
                                gr.Markdown("文档库", elem_classes=["docqa-hero-title"])
                                gr.Markdown(
                                    "管理文档、查看索引状态，并选择下一次问答的范围。",
                                    elem_classes=["docqa-hero-copy"],
                                )
                            with gr.Column(elem_classes=["docqa-library-header-actions"]):
                                upload = gr.File(
                                    label="上传文档",
                                    file_types=[".pdf", ".md", ".markdown"],
                                    type="filepath",
                                    elem_classes=["docqa-upload", "docqa-upload-trigger"],
                                )
                                index_button = gr.Button(
                                    "开始索引",
                                    elem_classes=["docqa-library-index"],
                                )
                                document_status = gr.Markdown(
                                    "等待选择 PDF 或 Markdown",
                                    elem_classes=["docqa-status", "docqa-library-status"],
                                )
                        with gr.Column(elem_classes=["docqa-library-toolbar"]):
                            document_search = gr.Textbox(
                                label="搜索",
                                placeholder="搜索文档名或 document_id",
                                show_label=False,
                                elem_classes=["docqa-library-search", "docqa-library-search-field"],
                            )
                            with gr.Row(elem_classes=["docqa-library-filter-bar"]):
                                document_format = gr.Dropdown(
                                    ["全部格式", "PDF", "MARKDOWN"],
                                    value="全部格式",
                                    label="格式",
                                    show_label=False,
                                    elem_classes=["docqa-library-filter", "docqa-library-filter-control"],
                                )
                                document_status_filter = gr.Dropdown(
                                    ["全部状态", "indexed", "archived", "failed", "deleted", "inconsistent"],
                                    value="全部状态",
                                    label="状态",
                                    show_label=False,
                                    elem_classes=["docqa-library-filter", "docqa-library-filter-control"],
                                )
                                document_sort = gr.Dropdown(
                                    [
                                        ("最近更新", "updated_desc"),
                                        ("最早更新", "updated_asc"),
                                        ("文档名", "name_asc"),
                                    ],
                                    value="updated_desc",
                                    label="排序",
                                    show_label=False,
                                    elem_classes=["docqa-library-filter", "docqa-library-filter-control"],
                                )
                                library_count = gr.Markdown(
                                    controller.document_library_count(),
                                    elem_classes=["docqa-library-count"],
                                )
                        with gr.Column(elem_classes=["docqa-library-list-panel"]):
                            with gr.Row(elem_classes=["docqa-library-list-heading"]):
                                with gr.Column():
                                    gr.Markdown("全部文档", elem_classes=["docqa-library-list-title"])
                                    gr.Markdown(
                                        "文档名、格式、状态和更新时间",
                                        elem_classes=["docqa-library-list-copy"],
                                    )
                            document_library = gr.HTML(
                                value=controller.document_library_markup(
                                    selected_document_id=initial_document_detail_id
                                ),
                                elem_classes=["docqa-document-library"],
                            )
                        document_table = gr.Dataframe(
                            headers=["文档", "格式", "状态", "更新时间"],
                            datatype=["str"] * 4,
                            value=[],
                            interactive=False,
                            wrap=True,
                            line_breaks=True,
                            column_widths=["2fr", "0.8fr", "1fr", "1.3fr"],
                            show_fullscreen_button=False,
                            show_copy_button=False,
                            show_row_numbers=False,
                            label=None,
                            visible=False,
                            elem_classes=["docqa-document-table", "docqa-document-table-compat"],
                        )
                        gr.Markdown(
                            "点击学习会话进入问答；完整 document_id、hash、定位方案和错误详情在右侧检查器查看。",
                            elem_classes=["docqa-hero-copy"],
                        )
                    with gr.Group(visible=True, elem_id="session-view", elem_classes=["docqa-session-view"]) as session_view:
                        with gr.Row(elem_classes=["docqa-session-header"]):
                            with gr.Column(elem_classes=["docqa-session-intro"]):
                                gr.Markdown("学习会话", elem_classes=["docqa-eyebrow"])
                                gr.Markdown("把问题问清楚，再回到原文", elem_classes=["docqa-hero-title"])
                                gr.Markdown(
                                    "回答必须绑定当前文档范围，并保留可追溯来源。",
                                    elem_classes=["docqa-hero-copy"],
                                )
                                with gr.Row(elem_classes=["docqa-session-chip-row"]):
                                    document_filter = gr.Dropdown(
                                        choices=[("全部文档", "")],
                                        label="当前问答范围",
                                        value="",
                                        show_label=False,
                                        elem_classes=["docqa-session-filter", "docqa-session-filter-chip"],
                                    )
                                    session_status = gr.Markdown("正在初始化", elem_classes=["docqa-status"])
                                    scope_status = gr.Markdown(
                                        "当前范围：全部文档",
                                        visible=False,
                                        elem_classes=["docqa-status", "docqa-scope"],
                                    )
                            new_session_button = gr.Button(
                                "+ 新会话",
                                elem_classes=["docqa-header-action"],
                            )
                        with gr.Column(elem_classes=["docqa-session-workspace"]):
                            with gr.Column(elem_classes=["docqa-timeline-panel"]):
                                with gr.Row(elem_classes=["docqa-timeline-heading"]):
                                    gr.Markdown("对话时间线", elem_classes=["docqa-eyebrow"])
                                    gr.Markdown("问题 · 回答 · 来源", elem_classes=["docqa-session-meta"])
                                chatbot = gr.Chatbot(
                                    label="问答记录",
                                    type="messages",
                                    placeholder="先从一个问题开始；回答会显示在这里。",
                                    show_label=False,
                                    visible=False,
                                    elem_classes=["docqa-chatbot"],
                                )
                                conversation_timeline = gr.HTML(
                                    _format_session_timeline([], "等待提问", {}),
                                    elem_classes=["docqa-timeline-render"],
                                )
                                answer_status = gr.Markdown(
                                    "等待提问",
                                    visible=False,
                                    elem_classes=["docqa-answer-status", "docqa-status"],
                                )
                            with gr.Column(elem_classes=["docqa-composer"]):
                                with gr.Row(elem_classes=["docqa-composer-main"]):
                                    question = gr.Textbox(
                                        label="向当前范围提问",
                                        placeholder="向当前文档提问…",
                                        lines=1,
                                        show_label=False,
                                        elem_classes=["docqa-composer-input"],
                                    )
                                    ask_button = gr.Button("↑", variant="primary", elem_classes=["docqa-composer-send"])
                                with gr.Row(elem_classes=["docqa-composer-footer"]):
                                    gr.Markdown(
                                        "当前范围：全部文档 · Enter 发送 · Shift + Enter 换行",
                                        elem_classes=["docqa-session-meta", "docqa-composer-hint"],
                                    )
                                    clear_button = gr.Button("清空", elem_classes=["docqa-composer-clear"])

                with gr.Column(scale=0, min_width=340, elem_classes=["docqa-inspector"], elem_id="sources-panel") as sources_panel:
                    gr.HTML(
                        '<span class="docqa-sheet-handle-mark" aria-hidden="true"></span>',
                        elem_classes=["docqa-sheet-handle"],
                    )
                    with gr.Column(elem_classes=["docqa-inspector-header"]):
                        with gr.Row(elem_classes=["docqa-inspector-heading-row"]):
                            with gr.Column(elem_classes=["docqa-inspector-heading-copy"]):
                                gr.Markdown("上下文检查器", elem_classes=["docqa-eyebrow", "docqa-inspector-eyebrow"])
                                inspector_title = gr.Markdown("来源与复习", elem_classes=["docqa-hero-title"])
                            close_context_button = gr.Button(
                                "关闭",
                                variant="secondary",
                                elem_classes=["docqa-context-close"],
                            )
                        inspector_copy = gr.Markdown(
                            "回答中的证据按文档类型显示定位方式。",
                            elem_classes=["docqa-hero-copy", "docqa-inspector-copy"],
                        )
                    with gr.Group(visible=True, elem_classes=["docqa-context-view"]) as context_view:
                      with gr.Column(elem_classes=["docqa-inspector-body"]):
                        with gr.Tabs(elem_classes=["docqa-context-tabs"]):
                            with gr.Tab("来源", id="sources-tab"):
                                source_summary = gr.HTML(
                                    _format_source_cards([]),
                                    elem_classes=["docqa-source-summary"],
                                )
                                gr.Markdown(
                                    "定位信息保持原文语义，不把 Markdown 伪装成页码。",
                                    elem_classes=["docqa-mobile-locator-note"],
                                )
                                with gr.Accordion(
                                    "查看原始引用数据",
                                    open=False,
                                    elem_classes=["docqa-raw-source"],
                                ):
                                    sources = gr.JSON(label=None, value={})
                                gr.Markdown("学习笔记", elem_classes=["docqa-inspector-section-title"])
                                inspector_note_preview = gr.HTML(
                                    controller.note_list_markup(None),
                                    elem_classes=["docqa-inspector-note-preview"],
                                )
                                inspector_scope = gr.HTML(
                                    '<div class="docqa-inspector-scope-card"><span>当前范围</span><strong>全部文档</strong></div>',
                                    elem_classes=["docqa-inspector-scope"],
                                )
                            with gr.Tab("笔记", id="notes-tab"):
                                with gr.Column(elem_classes=["docqa-notes-card", "docqa-note-editor"]):
                                    gr.Markdown("学习笔记", elem_classes=["docqa-eyebrow"])
                                    note_content = gr.Textbox(
                                        label="笔记内容",
                                        lines=4,
                                        placeholder="记录你的理解、疑问或下一步行动",
                                        elem_classes=["docqa-note-content"],
                                    )
                                    save_note_button = gr.Button(
                                        "保存为笔记",
                                        variant="primary",
                                        elem_classes=["docqa-note-save"],
                                    )
                                    note_status = gr.Markdown("等待保存笔记", elem_classes=["docqa-status", "docqa-note-status"])
                                    note_selector = gr.Dropdown(
                                        choices=[],
                                        label="选择已有笔记",
                                        elem_classes=["docqa-note-selector"],
                                    )
                                    update_note_button = gr.Button(
                                        "更新选中笔记",
                                        elem_classes=["docqa-note-update"],
                                    )
                                note_list_markup = gr.HTML(
                                    controller.note_list_markup(None),
                                    elem_classes=["docqa-note-list-markup"],
                                )
                                notes_table = gr.Dataframe(
                                    headers=["笔记 ID", "内容", "文档", "更新时间"],
                                    datatype=["str"] * 4,
                                    value=[],
                                    interactive=False,
                                    wrap=True,
                                    label="笔记列表",
                                    visible=False,
                                    elem_classes=["docqa-notes-table", "docqa-note-list"],
                                )
                    with gr.Group(visible=False, elem_id="document-inspector", elem_classes=["docqa-document-inspector"]) as document_inspector:
                        with gr.Column(elem_classes=["docqa-inspector-body"]):
                            document_detail_selector = gr.Dropdown(
                                choices=controller.document_choices(),
                                label="查看文档详情（不改变问答范围）",
                                value=initial_document_detail_id,
                                show_label=False,
                                elem_id="docqa-detail-selector",
                                elem_classes=["docqa-detail-selector", "docqa-detail-selector-controlled"],
                            )
                            document_inspector_markup = gr.HTML(
                                controller.document_inspector_markup(initial_document_detail_id),
                                elem_classes=["docqa-document-inspector-markup"],
                            )
                            document_detail_summary = gr.Markdown(
                                controller.document_detail_summary(initial_document_detail_id),
                                visible=False,
                                elem_classes=["docqa-detail-summary"],
                            )
                            document_detail = gr.JSON(
                                label="完整 document_id、hash、索引统计和错误详情",
                                value=controller.document_details(initial_document_detail_id),
                                visible=False,
                                elem_classes=["docqa-document-detail"],
                            )
                            with gr.Column(elem_classes=["docqa-danger-zone"]):
                                gr.Markdown(
                                    "**生命周期**\n\n归档保留向量；删除前必须确认，失败时保留既有文档状态。",
                                    elem_classes=["docqa-danger-copy"],
                                )
                                with gr.Row(elem_classes=["docqa-actions-row"]):
                                    archive_button = gr.Button("归档")
                                    unarchive_button = gr.Button("取消归档")
                                with gr.Row(elem_classes=["docqa-actions-row"]):
                                    restore_button = gr.Button("重新索引恢复")
                                    delete_button = gr.Button("删除文档", variant="stop")
                                delete_confirm = gr.Checkbox(
                                    label="确认删除 Qdrant points；SQLite 历史保留",
                                    value=False,
                                )

            with gr.Accordion(
                "学习统计与报告",
                open=False,
                visible=False,
                elem_classes=["docqa-stats"],
            ) as stats_section:
                with gr.Row():
                    start_date = gr.Textbox(label="开始日期", placeholder="YYYY-MM-DD")
                    end_date = gr.Textbox(label="结束日期", placeholder="YYYY-MM-DD")
                    stats_button = gr.Button("刷新统计")
                stats_json = gr.JSON(label="统计", value=_empty_stats())
                report_json = gr.JSON(label="确定性报告", value={})

        clear_button.click(lambda: "", outputs=[question])
        load_event = demo.load(
            controller.initialize,
            outputs=[session_state, session_status, chatbot, sources, document_table, stats_json],
        )
        load_event.then(
            initial_view,
            outputs=[
                library_view,
                session_view,
                nav_library_button,
                nav_session_button,
                context_view,
                document_inspector,
                mobile_nav_toggle,
                mobile_context_toggle,
                inspector_title,
                inspector_copy,
            ],
        )
        load_event.then(
            _format_session_timeline,
            inputs=[chatbot, answer_status, sources],
            outputs=[conversation_timeline],
        )
        load_event.then(controller.note_list_markup, inputs=[session_state], outputs=[note_list_markup])
        demo.load(controller.refresh_document_choices, outputs=[document_filter])
        detail_load_event = demo.load(
            controller.refresh_document_detail_selector,
            outputs=[document_detail_selector],
        )
        detail_load_event.then(
            controller.document_inspector_markup,
            inputs=[document_detail_selector],
            outputs=[document_inspector_markup],
        )
        demo.load(
            controller.document_library_markup,
            inputs=[document_search, document_format, document_status_filter, document_sort, document_detail_selector],
            outputs=[document_library],
        )
        demo.load(controller.document_library_count, outputs=[library_count])
        for control in [document_search, document_format, document_status_filter, document_sort]:
            filter_event = control.change(
                controller.filter_document_table_rows,
                inputs=[document_search, document_format, document_status_filter, document_sort],
                outputs=[document_table],
            )
            filter_event.then(
                controller.document_library_markup,
                inputs=[document_search, document_format, document_status_filter, document_sort, document_detail_selector],
                outputs=[document_library],
            )
            filter_event.then(
                controller.document_library_count,
                inputs=[document_search, document_format, document_status_filter, document_sort],
                outputs=[library_count],
            )
        index_event = index_button.click(
            controller.index_document_table,
            inputs=[upload],
            outputs=[document_status, document_table, document_filter],
            show_progress="full",
        )
        index_scope_event = index_event.then(
            controller.switch_document_scope,
            inputs=[document_filter],
            outputs=[scope_status, answer_status, chatbot, sources, source_summary, current_turn_state, source_locator_state, notes_table, note_selector, note_content],
        )
        index_scope_event.then(
            _format_session_timeline,
            inputs=[chatbot, answer_status, sources],
            outputs=[conversation_timeline],
        )
        index_detail_event = index_event.then(
            controller.refresh_document_detail_selector,
            outputs=[document_detail_selector],
        )
        index_detail_event.then(
            controller.document_details,
            inputs=[document_detail_selector],
            outputs=[document_detail],
        )
        index_detail_event.then(
            controller.document_detail_summary,
            inputs=[document_detail_selector],
            outputs=[document_detail_summary],
        )
        index_detail_event.then(
            controller.document_inspector_markup,
            inputs=[document_detail_selector],
            outputs=[document_inspector_markup],
        )
        index_event.then(controller.recent_document_markup, outputs=[recent_documents])
        index_event.then(controller.document_library_markup, outputs=[document_library])
        index_event.then(controller.document_library_count, outputs=[library_count])
        scope_change_event = document_filter.change(
            controller.switch_document_scope,
            inputs=[document_filter],
            outputs=[scope_status, answer_status, chatbot, sources, source_summary, current_turn_state, source_locator_state, notes_table, note_selector, note_content],
        )
        scope_change_event.then(
            _format_session_timeline,
            inputs=[chatbot, answer_status, sources],
            outputs=[conversation_timeline],
        )
        scope_change_event.then(controller.note_list_markup, inputs=[session_state], outputs=[note_list_markup])
        scope_change_event.then(controller.note_list_markup, inputs=[session_state], outputs=[inspector_note_preview])
        document_filter.change(
            lambda value: f"范围 · {value or '全部文档'}",
            inputs=[document_filter],
            outputs=[topbar_scope],
        )
        document_filter.change(
            lambda value: (
                '<div class="docqa-inspector-scope-card"><span>当前范围</span>'
                f'<strong>{escape(str(value or "全部文档"))}</strong></div>'
            ),
            inputs=[document_filter],
            outputs=[inspector_scope],
        )
        document_detail_selector.change(controller.document_details, inputs=[document_detail_selector], outputs=[document_detail])
        document_detail_selector.change(controller.document_detail_summary, inputs=[document_detail_selector], outputs=[document_detail_summary])
        document_detail_selector.change(
            controller.document_inspector_markup,
            inputs=[document_detail_selector],
            outputs=[document_inspector_markup],
        )
        document_detail_selector.change(
            controller.document_library_markup,
            inputs=[document_search, document_format, document_status_filter, document_sort, document_detail_selector],
            outputs=[document_library],
        )
        document_row_event = document_library.click(
            select_document_detail,
            inputs=[document_detail_selector],
            outputs=[
                document_detail_selector,
                document_detail,
                document_detail_summary,
                document_inspector_markup,
            ],
            js="(current) => [window.__docqaSelectedDocumentId || current]",
            show_progress="hidden",
        )
        document_row_event.then(
            controller.document_library_markup,
            inputs=[document_search, document_format, document_status_filter, document_sort, document_detail_selector],
            outputs=[document_library],
        )
        lifecycle_outputs = [document_status, document_table, document_filter, document_detail, document_detail_summary]
        for action_button, action in [
            (archive_button, "archive"),
            (unarchive_button, "unarchive"),
            (restore_button, "restore"),
        ]:
            lifecycle_event = action_button.click(
                lambda document_id, selected_action=action: controller._lifecycle_table_result(selected_action, document_id),
                inputs=[document_detail_selector],
                outputs=lifecycle_outputs,
            )
            lifecycle_detail_event = lifecycle_event.then(
                controller.refresh_document_detail_selector,
                outputs=[document_detail_selector],
            )
            lifecycle_detail_event.then(
                controller.document_inspector_markup,
                inputs=[document_detail_selector],
                outputs=[document_inspector_markup],
            )
            lifecycle_event.then(controller.recent_document_markup, outputs=[recent_documents])
            lifecycle_event.then(controller.document_library_markup, outputs=[document_library])
            lifecycle_event.then(controller.document_library_count, outputs=[library_count])
        delete_event = delete_button.click(
            lambda document_id, confirm: controller._lifecycle_table_result("delete", document_id, confirm),
            inputs=[document_detail_selector, delete_confirm],
            outputs=lifecycle_outputs,
        )
        delete_detail_event = delete_event.then(
            controller.refresh_document_detail_selector,
            outputs=[document_detail_selector],
        )
        delete_detail_event.then(
            controller.document_inspector_markup,
            inputs=[document_detail_selector],
            outputs=[document_inspector_markup],
        )
        delete_event.then(controller.recent_document_markup, outputs=[recent_documents])
        delete_event.then(controller.document_library_markup, outputs=[document_library])
        delete_event.then(controller.document_library_count, outputs=[library_count])
        workspace_outputs = [
            library_view,
            session_view,
            nav_library_button,
            nav_session_button,
            context_view,
            document_inspector,
            mobile_nav_toggle,
            mobile_context_toggle,
            inspector_title,
            inspector_copy,
            stats_section,
        ]
        report_outputs = [
            library_view,
            session_view,
            nav_library_button,
            nav_session_button,
            stats_section,
            context_view,
            document_inspector,
            mobile_nav_toggle,
            mobile_context_toggle,
            inspector_title,
            inspector_copy,
        ]
        nav_library_button.click(show_library, outputs=workspace_outputs)
        nav_session_button.click(show_session, outputs=workspace_outputs)
        nav_context_button.click(show_context, outputs=workspace_outputs)
        nav_reports_button.click(show_reports, outputs=report_outputs)
        close_context_button.click(
            lambda: gr.update(value=False),
            outputs=[mobile_context_toggle],
            show_progress="hidden",
        )
        new_session_event = new_session_button.click(
            controller.new_session,
            outputs=[session_state, session_status, chatbot, sources, source_summary, answer_status, current_turn_state, source_locator_state, notes_table, note_selector, note_content, stats_json],
        )
        new_session_event.then(
            _format_session_timeline,
            inputs=[chatbot, answer_status, sources],
            outputs=[conversation_timeline],
        )
        new_session_event.then(controller.note_list_markup, inputs=[session_state], outputs=[note_list_markup])
        new_session_event.then(controller.note_list_markup, inputs=[session_state], outputs=[inspector_note_preview])
        new_session_button.click(lambda: "全部文档", outputs=[topbar_scope])
        ask_outputs = [session_state, chatbot, answer_status, sources, source_summary, current_turn_state, source_locator_state, notes_table, note_selector, stats_json]
        ask_event = ask_button.click(
            controller.ask,
            inputs=[session_state, question, document_filter, chatbot],
            outputs=ask_outputs,
            show_progress="full",
        )
        ask_event.then(
            _format_session_timeline,
            inputs=[chatbot, answer_status, sources],
            outputs=[conversation_timeline],
        )
        ask_event.then(controller.note_list_markup, inputs=[session_state], outputs=[note_list_markup])
        ask_event.then(controller.note_list_markup, inputs=[session_state], outputs=[inspector_note_preview])
        submit_event = question.submit(
            controller.ask,
            inputs=[session_state, question, document_filter, chatbot],
            outputs=ask_outputs,
            show_progress="full",
        )
        submit_event.then(
            _format_session_timeline,
            inputs=[chatbot, answer_status, sources],
            outputs=[conversation_timeline],
        )
        submit_event.then(controller.note_list_markup, inputs=[session_state], outputs=[note_list_markup])
        submit_event.then(controller.note_list_markup, inputs=[session_state], outputs=[inspector_note_preview])
        ask_event.then(lambda: "", outputs=[question])
        submit_event.then(lambda: "", outputs=[question])
        save_note_event = save_note_button.click(
            controller.save_note,
            inputs=[session_state, current_turn_state, document_filter, source_locator_state, note_content],
            outputs=[note_status, notes_table, note_selector, note_content],
        )
        save_note_event.then(controller.note_list_markup, inputs=[session_state], outputs=[note_list_markup])
        save_note_event.then(controller.note_list_markup, inputs=[session_state], outputs=[inspector_note_preview])
        note_selector.change(controller.load_note, inputs=[note_selector, session_state], outputs=[note_content])
        update_note_event = update_note_button.click(
            controller.update_note,
            inputs=[note_selector, note_content, session_state],
            outputs=[note_status, notes_table],
        )
        update_note_event.then(controller.note_list_markup, inputs=[session_state], outputs=[note_list_markup])
        update_note_event.then(controller.note_list_markup, inputs=[session_state], outputs=[inspector_note_preview])
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
