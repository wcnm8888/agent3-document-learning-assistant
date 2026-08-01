from __future__ import annotations

from datetime import date
from pathlib import Path
import sqlite3

import pytest

from doc_qa.config import Settings
from doc_qa.errors import NoteValidationError, SessionNotFoundError
from doc_qa.learning import LearningService
from doc_qa.memory_store import SQLiteMemoryStore
from doc_qa.models import AnswerResponse, Citation


class FakeQA:
    model_name = "deepseek-v4-flash"

    def __init__(self):
        self.contexts: list[list[dict[str, str]]] = []

    def ask(self, question: str, *, document_id=None, conversation_context=None):
        context = list(conversation_context or [])
        self.contexts.append(context)
        if "无答案" in question:
            return AnswerResponse(
                status="no_results",
                question=question,
                answer="根据当前文档片段不足以回答这个问题。",
                citations=[],
                retrieved_count=0,
                model=self.model_name,
            )
        citation = Citation(
            citation_id="S1",
            document_id=document_id or "doc-happy",
            document_name="Happy-LLM-0727.pdf",
            chunk_id="chunk-1",
            section="第一章",
            page_start=2,
            page_end=2,
            source_locator="Happy-LLM-0727.pdf#page=2&chunk=chunk-1",
            score=0.8,
            content="文档片段内容",
        )
        return AnswerResponse(
            status="answered",
            question=question,
            answer="文档支持这个结论。[S1]",
            citations=[citation],
            retrieved_count=1,
            model=self.model_name,
        )


def _settings(db_path: Path, *, limit: int = 6, max_chars: int = 4000) -> Settings:
    return Settings(
        embedding_model="text-embedding-v4",
        embedding_dimension=1024,
        sqlite_path=db_path,
        memory_turn_limit=limit,
        memory_context_max_chars=max_chars,
    )


def test_session_history_persists_and_isolated(tmp_path: Path):
    db_path = tmp_path / "learning.sqlite3"
    fake = FakeQA()
    service = LearningService(_settings(db_path), qa_service=fake)
    session_a = service.create_session("session-a")
    session_b = service.create_session("session-b")

    first = service.ask(session_a.session_id, "第一轮问题")
    service.ask(session_a.session_id, "第二轮追问")
    service.ask(session_b.session_id, "另一会话问题")

    assert first.status == "answered"
    assert len(fake.contexts[0]) == 0
    assert len(fake.contexts[1]) == 1
    assert fake.contexts[1][0]["question"] == "第一轮问题"
    assert len(fake.contexts[2]) == 0
    assert len(service.get_history(session_a.session_id)) == 2
    service.close()

    with SQLiteMemoryStore(db_path) as reopened:
        assert len(reopened.list_turns(session_a.session_id)) == 2
        assert reopened.integrity_check() == "ok"


def test_memory_window_limits_turn_count_and_chars(tmp_path: Path):
    fake = FakeQA()
    service = LearningService(_settings(tmp_path / "memory.sqlite3", limit=2, max_chars=20), qa_service=fake)
    session = service.create_session()
    service.ask(session.session_id, "a" * 10)
    service.ask(session.session_id, "b" * 10)
    service.ask(session.session_id, "c" * 10)

    assert len(fake.contexts[-1]) == 1
    assert fake.contexts[-1][0]["question"] == "b" * 10
    service.close()


def test_notes_sources_events_and_stats(tmp_path: Path):
    fake = FakeQA()
    service = LearningService(_settings(tmp_path / "notes.sqlite3"), qa_service=fake)
    session = service.create_session()
    response = service.ask(session.session_id, "事实问题", document_id="doc-happy")
    turn = service.get_history(session.session_id)[0]
    citation = response.citations[0]

    note = service.create_note(
        session.session_id,
        "先记住这一条",
        turn_id=turn.turn_id,
        document_id=citation.document_id,
        source_locator=citation.source_locator,
    )
    updated = service.update_note(note.note_id, "已经复习并补充这一条")
    service.ask(session.session_id, "无答案问题")
    stats = service.stats(date.today().isoformat(), date.today().isoformat())
    report = service.report(date.today().isoformat(), date.today().isoformat()).report

    assert updated.content == "已经复习并补充这一条"
    assert len(service.list_notes(session.session_id)) == 1
    assert stats.question_count == 2
    assert stats.answered_count == 1
    assert stats.no_results_count == 1
    assert stats.note_count == 1
    assert stats.document_count == 1
    event_types = {item["event_type"] for item in stats.daily_events}
    assert {"session_created", "question_asked", "answer_generated", "no_results", "note_created", "note_updated"} <= event_types
    assert report["statistics"] == stats.as_dict()
    service.close()


def test_invalid_note_references_are_rejected(tmp_path: Path):
    service = LearningService(_settings(tmp_path / "invalid.sqlite3"), qa_service=FakeQA())
    session = service.create_session()
    service.ask(session.session_id, "事实问题", document_id="doc-happy")
    turn = service.get_history(session.session_id)[0]

    with pytest.raises(NoteValidationError, match="不能为空"):
        service.create_note(session.session_id, " ")
    with pytest.raises(NoteValidationError, match="document_id"):
        service.create_note(session.session_id, "错误文档", turn_id=turn.turn_id, document_id="other-doc")
    with pytest.raises(SessionNotFoundError):
        service.create_note("missing-session", "没有会话")
    service.close()


def test_database_initializes_missing_parent_and_rejects_bad_dates(tmp_path: Path):
    db_path = tmp_path / "nested" / "learning.sqlite3"
    store = SQLiteMemoryStore(db_path)
    assert db_path.exists()
    with pytest.raises(NoteValidationError, match="YYYY-MM-DD"):
        store.stats("2026/01/01", None)
    store.close()


def test_legacy_citations_schema_migrates_nullable_markdown_pages(tmp_path: Path):
    db_path = tmp_path / "legacy-citations.sqlite3"
    connection = sqlite3.connect(db_path)
    connection.executescript(
        """
        CREATE TABLE sessions (session_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE conversation_turns (
            turn_id TEXT PRIMARY KEY, session_id TEXT NOT NULL,
            turn_index INTEGER NOT NULL, question TEXT NOT NULL, answer TEXT NOT NULL,
            status TEXT NOT NULL, model TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE TABLE citations (
            citation_row_id INTEGER PRIMARY KEY AUTOINCREMENT,
            turn_id TEXT NOT NULL, citation_id TEXT NOT NULL, document_id TEXT NOT NULL,
            document_name TEXT NOT NULL, chunk_id TEXT NOT NULL, section TEXT NOT NULL,
            page_start INTEGER NOT NULL, page_end INTEGER NOT NULL,
            source_locator TEXT NOT NULL, score REAL NOT NULL, content TEXT NOT NULL
        );
        """
    )
    connection.commit()
    connection.close()

    store = SQLiteMemoryStore(db_path)
    columns = {row[1]: row for row in store._connection.execute("PRAGMA table_info(citations)")}
    assert columns["page_start"][3] == 0
    assert columns["page_end"][3] == 0
    assert store.integrity_check() == "ok"
    store.close()


def test_markdown_citation_with_null_pages_persists_and_reloads(tmp_path: Path):
    db_path = tmp_path / "markdown-citation.sqlite3"
    store = SQLiteMemoryStore(db_path)
    session_id = store.create_session("Markdown 测试").session_id
    response = AnswerResponse(
        status="answered",
        question="Markdown 的来源如何定位？",
        answer="依据章节和行号回答。[S1]",
        citations=[
            Citation(
                citation_id="S1",
                document_id="doc-markdown",
                document_name="guide.md",
                chunk_id="chunk-1",
                section="安装",
                page_start=None,
                page_end=None,
                source_locator="guide.md#section=安装&lines=3-5&chunk=chunk-1",
                score=0.9,
                content="安装步骤",
            )
        ],
        retrieved_count=1,
        model="deepseek-chat",
    )

    saved = store.save_turn(session_id, response)
    reloaded = store.list_turns(session_id)[0]

    assert saved.citations[0].page_start is None
    assert saved.citations[0].page_end is None
    assert reloaded.citations[0].page_start is None
    assert reloaded.citations[0].page_end is None
    assert "lines=3-5" in reloaded.citations[0].source_locator
    assert store.integrity_check() == "ok"
    store.close()
