from __future__ import annotations

from datetime import date
from pathlib import Path
import sqlite3

import pytest

from doc_qa.config import Settings
from doc_qa.errors import NoteValidationError, SessionNotFoundError
from doc_qa.learning import ContextCandidates, LearningService
from doc_qa.memory_store import ConversationContextCandidate, SQLiteMemoryStore
from doc_qa.models import AnswerResponse, Citation


class FakeQA:
    model_name = "deepseek-v4-flash"

    def __init__(self):
        self.contexts: list[list[dict[str, str]]] = []
        self.note_batches: list[list[object]] = []

    def ask(self, question: str, *, document_id=None, conversation_context=None, notes=None):
        context = [
            {
                "question": (
                    item.get("question", "")
                    if isinstance(item, dict)
                    else getattr(item, "question", "")
                ),
                "answer": (
                    item.get("answer", "")
                    if isinstance(item, dict)
                    else getattr(item, "answer", "")
                ),
            }
            for item in (conversation_context or [])
        ]
        self.contexts.append(context)
        self.note_batches.append(list(notes or []))
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


def _response(question: str, answer: str) -> AnswerResponse:
    return AnswerResponse(
        status="answered",
        question=question,
        answer=answer,
        citations=[],
        retrieved_count=0,
        model="test-model",
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


def test_context_history_candidates_are_session_isolated_and_keep_latest_turn(tmp_path: Path):
    store = SQLiteMemoryStore(tmp_path / "context-history.sqlite3")
    session_a = store.create_session("session-context-a")
    session_b = store.create_session("session-context-b")
    first = store.save_turn(session_a.session_id, _response("a", "1"))
    second = store.save_turn(session_a.session_id, _response("bb", "22"))
    third = store.save_turn(session_a.session_id, _response("ccc", "333"))
    store.save_turn(session_b.session_id, _response("other", "session"))

    candidates = store.context_history_candidates(
        session_a.session_id,
        limit=2,
        max_chars=10,
    )
    constrained = store.context_history_candidates(
        session_a.session_id,
        limit=2,
        max_chars=5,
    )

    assert candidates == [
        ConversationContextCandidate(
            turn_id=second.turn_id,
            session_id=session_a.session_id,
            turn_index=2,
            question="bb",
            answer="22",
            created_at=second.created_at,
        ),
        ConversationContextCandidate(
            turn_id=third.turn_id,
            session_id=session_a.session_id,
            turn_index=3,
            question="ccc",
            answer="333",
            created_at=third.created_at,
        ),
    ]
    assert constrained == [candidates[1]]
    assert sum(len(item.question) + len(item.answer) for item in candidates) <= 10
    assert len(constrained[0].question) + len(constrained[0].answer) > 5
    assert all(item.session_id == session_a.session_id for item in candidates)
    assert all(not hasattr(item, "citations") for item in candidates)
    assert first.turn_id not in {item.turn_id for item in candidates}
    store.close()


def test_context_note_candidates_enforce_session_scope_limit_and_budget(tmp_path: Path):
    service = LearningService(_settings(tmp_path / "context-notes.sqlite3"), qa_service=FakeQA())
    session_a = service.create_session("session-notes-a")
    session_b = service.create_session("session-notes-b")
    service.ask(session_a.session_id, "文档 A", document_id="doc-a")
    service.ask(session_a.session_id, "文档 B", document_id="doc-b")
    turns = service.get_history(session_a.session_id)
    note_a = service.create_note(
        session_a.session_id,
        "A 笔记",
        turn_id=turns[0].turn_id,
        document_id="doc-a",
    )
    note_b = service.create_note(
        session_a.session_id,
        "B 笔记",
        turn_id=turns[1].turn_id,
        document_id="doc-b",
    )
    general = service.create_note(session_a.session_id, "通用笔记")
    service.create_note(session_b.session_id, "其他会话笔记")

    scoped = service.store.context_note_candidates(
        session_a.session_id,
        document_id="doc-a",
        limit=3,
        max_chars=100,
    )
    unscoped = service.store.context_note_candidates(
        session_a.session_id,
        document_id=None,
        limit=3,
        max_chars=100,
    )
    constrained = service.store.context_note_candidates(
        session_a.session_id,
        document_id=None,
        limit=2,
        max_chars=len(general.content) + len(note_b.content),
    )

    assert {item.note_id for item in scoped} == {note_a.note_id, general.note_id}
    assert note_b.note_id not in {item.note_id for item in scoped}
    assert {item.note_id for item in unscoped} == {
        note_a.note_id,
        note_b.note_id,
        general.note_id,
    }
    assert unscoped == service.store.context_note_candidates(
        session_a.session_id,
        document_id=None,
        limit=3,
        max_chars=100,
    )
    assert len(constrained) <= 2
    constrained_chars = sum(len(item.content) for item in constrained)
    assert constrained_chars <= len(general.content) + len(note_b.content)
    assert service.store.context_note_candidates(
        session_a.session_id,
        document_id=None,
        limit=3,
        max_chars=1,
    ) == []
    assert all(item.session_id == session_a.session_id for item in unscoped)
    service.close()


def test_learning_service_exposes_immutable_context_candidates_without_qa_integration(
    tmp_path: Path,
):
    fake = FakeQA()
    service = LearningService(
        _settings(tmp_path / "context-candidates.sqlite3", limit=2, max_chars=100),
        qa_service=fake,
    )
    session = service.create_session("session-candidates")
    service.ask(session.session_id, "第一轮", document_id="doc-a")
    turn = service.get_history(session.session_id)[0]
    note = service.create_note(
        session.session_id,
        "学习笔记",
        turn_id=turn.turn_id,
        document_id="doc-a",
    )
    qa_calls_before = len(fake.contexts)

    candidates = service.get_context_candidates(session.session_id, document_id="doc-a")

    assert isinstance(candidates, ContextCandidates)
    assert isinstance(candidates.conversation_history, tuple)
    assert isinstance(candidates.notes, tuple)
    assert candidates.conversation_history[0].turn_id == turn.turn_id
    assert candidates.notes == (note,)
    assert len(fake.contexts) == qa_calls_before
    service.close()


def test_learning_ask_keeps_explicit_scope_history_and_adds_scoped_notes(tmp_path: Path):
    fake = FakeQA()
    service = LearningService(_settings(tmp_path / "learning-context.sqlite3"), qa_service=fake)
    session = service.create_session("session-learning-context")
    service.ask(session.session_id, "旧范围问题", document_id="doc-a")
    first_turn = service.get_history(session.session_id)[0]
    note = service.create_note(
        session.session_id,
        "当前文档笔记",
        turn_id=first_turn.turn_id,
        document_id="doc-a",
    )

    service.ask(
        session.session_id,
        "切换范围后的问题",
        document_id="doc-a",
        conversation_context=[],
    )

    assert fake.contexts[-1] == []
    assert fake.note_batches[-1] == [note]

    service.ask(session.session_id, "CLI 会话追问", document_id="doc-a")
    assert len(fake.contexts[-1]) == 2
    assert fake.note_batches[-1] == [note]
    service.close()


def test_context_candidate_reads_do_not_change_schema_or_persisted_data(tmp_path: Path):
    store = SQLiteMemoryStore(tmp_path / "context-read-only.sqlite3")
    session = store.create_session("session-read-only")
    store.save_turn(session.session_id, _response("问题", "回答"))
    store.create_note(session_id=session.session_id, content="只读笔记")
    schema_before = [
        tuple(row)
        for row in store._connection.execute(
            "SELECT type, name, tbl_name, sql FROM sqlite_master ORDER BY type, name"
        ).fetchall()
    ]
    data_version_before = store._connection.total_changes

    store.context_history_candidates(session.session_id, limit=6, max_chars=4000)
    store.context_note_candidates(
        session.session_id,
        document_id=None,
        limit=3,
        max_chars=2000,
    )

    schema_after = [
        tuple(row)
        for row in store._connection.execute(
            "SELECT type, name, tbl_name, sql FROM sqlite_master ORDER BY type, name"
        ).fetchall()
    ]
    assert schema_after == schema_before
    assert store._connection.total_changes == data_version_before
    assert store.integrity_check() == "ok"
    store.close()


def test_context_candidate_reads_reject_missing_session(tmp_path: Path):
    store = SQLiteMemoryStore(tmp_path / "context-missing-session.sqlite3")

    with pytest.raises(SessionNotFoundError):
        store.context_history_candidates("missing", limit=6, max_chars=4000)
    with pytest.raises(SessionNotFoundError):
        store.context_note_candidates(
            "missing",
            document_id=None,
            limit=3,
            max_chars=2000,
        )
    store.close()
