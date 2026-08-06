from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

from .config import Settings
from .memory_store import (
    ConversationContextCandidate,
    ConversationTurn,
    LearningStats,
    NoteRecord,
    SQLiteMemoryStore,
    SessionRecord,
)
from .models import AnswerResponse


class AskService(Protocol):
    def ask(
        self,
        question: str,
        *,
        document_id: str | None = None,
        conversation_context: Sequence[object] | None = None,
        notes: Sequence[object] | None = None,
    ) -> AnswerResponse: ...


@dataclass(frozen=True)
class LearningReport:
    report: dict[str, object]


@dataclass(frozen=True)
class ContextCandidates:
    """交给后续上下文编排层的只读 SQLite 候选集合。"""

    conversation_history: tuple[ConversationContextCandidate, ...]
    notes: tuple[NoteRecord, ...]


class LearningService:
    """编排 Phase 3 问答与 Phase 4 学习持久化，不直接依赖 UI。"""

    def __init__(
        self,
        settings: Settings,
        *,
        qa_service: AskService,
        store: SQLiteMemoryStore | None = None,
    ):
        self.settings = settings
        self.qa_service = qa_service
        self.store = store or SQLiteMemoryStore(settings.sqlite_path)

    def create_session(self, session_id: str | None = None) -> SessionRecord:
        return self.store.create_session(session_id)

    def ask(
        self,
        session_id: str,
        question: str,
        *,
        document_id: str | None = None,
        conversation_context: list[dict[str, str]] | None = None,
    ) -> AnswerResponse:
        candidates = self.get_context_candidates(session_id, document_id=document_id)
        context: Sequence[object] = (
            conversation_context
            if conversation_context is not None
            else candidates.conversation_history
        )
        response = self.qa_service.ask(
            question,
            document_id=document_id,
            conversation_context=context,
            notes=candidates.notes,
        )
        self.store.save_turn(session_id, response)
        return response

    def get_history(self, session_id: str) -> list[ConversationTurn]:
        return self.store.list_turns(session_id)

    def get_context_candidates(
        self,
        session_id: str,
        *,
        document_id: str | None = None,
    ) -> ContextCandidates:
        config = self.settings.context_config
        history = self.store.context_history_candidates(
            session_id,
            limit=config.history_turn_limit,
            max_chars=config.history_max_chars,
        )
        notes = self.store.context_note_candidates(
            session_id,
            document_id=document_id,
            limit=config.note_limit,
            max_chars=config.notes_max_chars,
        )
        return ContextCandidates(
            conversation_history=tuple(history),
            notes=tuple(notes),
        )

    def create_note(
        self,
        session_id: str,
        content: str,
        *,
        turn_id: str | None = None,
        document_id: str | None = None,
        source_locator: str | None = None,
    ) -> NoteRecord:
        return self.store.create_note(
            session_id=session_id,
            content=content,
            turn_id=turn_id,
            document_id=document_id,
            source_locator=source_locator,
        )

    def update_note(self, note_id: str, content: str) -> NoteRecord:
        return self.store.update_note(note_id, content)

    def list_notes(self, session_id: str | None = None) -> list[NoteRecord]:
        return self.store.list_notes(session_id)

    def stats(self, start_date: str | None = None, end_date: str | None = None) -> LearningStats:
        return self.store.stats(start_date, end_date)

    def report(self, start_date: str | None = None, end_date: str | None = None) -> LearningReport:
        return LearningReport(self.store.report(start_date, end_date))

    def close(self) -> None:
        self.store.close()
