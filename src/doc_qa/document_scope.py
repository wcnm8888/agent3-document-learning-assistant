from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentScopeState:
    """文档范围选择的无副作用状态；切换范围会清空临时问答状态。"""

    document_id: str | None = None
    conversation_context: tuple[dict[str, str], ...] = ()
    citations: tuple[dict[str, object], ...] = ()
    pending_note: str = ""

    def switch(self, document_id: str | None) -> "DocumentScopeState":
        normalized = document_id.strip() if document_id else None
        return DocumentScopeState(document_id=normalized or None)

    def all_documents(self) -> "DocumentScopeState":
        return self.switch(None)
