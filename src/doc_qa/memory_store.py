from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .errors import (
    DatabaseError,
    NoteNotFoundError,
    NoteValidationError,
    SessionNotFoundError,
)
from .models import AnswerResponse, Citation


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def _date_bounds(start_date: str | None, end_date: str | None) -> tuple[str | None, str | None]:
    try:
        start = date.fromisoformat(start_date) if start_date else None
        end = date.fromisoformat(end_date) if end_date else None
    except ValueError as exc:
        raise NoteValidationError("日期必须使用 YYYY-MM-DD 格式") from exc
    if start and end and start > end:
        raise NoteValidationError("统计开始日期不能晚于结束日期")
    # 用户输入的是本地日历日，而数据库统一保存 UTC 时间；先按本地时区
    # 构造闭开区间，再转换为 UTC，避免本地午夜附近漏统计或跨日统计。
    local_zone = datetime.now().astimezone().tzinfo

    def utc_start(day: date) -> str:
        local_datetime = datetime.combine(day, datetime.min.time(), tzinfo=local_zone)
        return local_datetime.astimezone(timezone.utc).isoformat()

    lower = utc_start(start) if start else None
    upper = utc_start(end + timedelta(days=1)) if end else None
    return lower, upper


@dataclass(frozen=True)
class SessionRecord:
    session_id: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class DocumentRecord:
    document_id: str
    document_name: str
    source_path: str
    pages_with_text: int
    chunk_count: int
    indexed_point_count: int
    status: str
    error_message: str | None
    updated_at: str
    format: str = "pdf"
    content_hash: str = ""
    embedding_model: str = "text-embedding-v4"
    embedding_dimension: int = 1024
    source_locator_scheme: str = "pdf-page-v1"
    source_unit_count: int = 0
    created_at: str = ""


@dataclass(frozen=True)
class ConversationTurn:
    turn_id: str
    session_id: str
    turn_index: int
    question: str
    answer: str
    status: str
    model: str
    created_at: str
    citations: list[Citation]


@dataclass(frozen=True)
class ConversationContextCandidate:
    """只供上下文理解使用的历史候选，不携带旧引用或事实资格。"""

    turn_id: str
    session_id: str
    turn_index: int
    question: str
    answer: str
    created_at: str


@dataclass(frozen=True)
class NoteRecord:
    note_id: str
    session_id: str
    turn_id: str | None
    document_id: str | None
    source_locator: str | None
    content: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class LearningStats:
    period_start: str | None
    period_end: str | None
    session_count: int
    question_count: int
    answered_count: int
    no_results_count: int
    note_count: int
    document_count: int
    daily_events: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "period_start": self.period_start,
            "period_end": self.period_end,
            "session_count": self.session_count,
            "question_count": self.question_count,
            "answered_count": self.answered_count,
            "no_results_count": self.no_results_count,
            "note_count": self.note_count,
            "document_count": self.document_count,
            "daily_events": self.daily_events,
        }


class SQLiteMemoryStore:
    """SQLite 持久化边界：会话、问答、来源、笔记和学习事件。"""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        if str(db_path) != ":memory:":
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._connection = sqlite3.connect(
                str(db_path), timeout=10, check_same_thread=False
            )
            self._connection.row_factory = sqlite3.Row
            self._lock = threading.RLock()
            self._configure()
            self._initialize_schema()
        except sqlite3.Error as exc:
            raise DatabaseError(f"SQLite 初始化失败: {exc}") from exc

    def _configure(self) -> None:
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute("PRAGMA busy_timeout = 10000")
        try:
            self._connection.execute("PRAGMA journal_mode = WAL")
        except sqlite3.Error:
            # 内存数据库等模式不支持 WAL，不阻断功能，但文件数据库仍优先使用 WAL。
            pass

    def _initialize_schema(self) -> None:
        schema = """
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS documents (
            document_id TEXT PRIMARY KEY,
            document_name TEXT NOT NULL,
            source_path TEXT NOT NULL,
            pages_with_text INTEGER NOT NULL DEFAULT 0,
            chunk_count INTEGER NOT NULL DEFAULT 0,
            indexed_point_count INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL,
            error_message TEXT,
            updated_at TEXT NOT NULL,
            format TEXT NOT NULL DEFAULT 'pdf',
            content_hash TEXT,
            embedding_model TEXT NOT NULL DEFAULT 'text-embedding-v4',
            embedding_dimension INTEGER NOT NULL DEFAULT 1024,
            source_locator_scheme TEXT NOT NULL DEFAULT 'pdf-page-v1',
            source_unit_count INTEGER NOT NULL DEFAULT 0,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS conversation_turns (
            turn_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
            turn_index INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('answered', 'no_results')),
            model TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(session_id, turn_index)
        );

        CREATE TABLE IF NOT EXISTS citations (
            citation_row_id INTEGER PRIMARY KEY AUTOINCREMENT,
            turn_id TEXT NOT NULL REFERENCES conversation_turns(turn_id) ON DELETE CASCADE,
            citation_id TEXT NOT NULL,
            document_id TEXT NOT NULL,
            document_name TEXT NOT NULL,
            chunk_id TEXT NOT NULL,
            section TEXT NOT NULL,
            page_start INTEGER NOT NULL,
            page_end INTEGER NOT NULL,
            source_locator TEXT NOT NULL,
            score REAL NOT NULL,
            content TEXT NOT NULL,
            UNIQUE(turn_id, citation_id)
        );

        CREATE TABLE IF NOT EXISTS notes (
            note_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
            turn_id TEXT REFERENCES conversation_turns(turn_id) ON DELETE SET NULL,
            document_id TEXT,
            source_locator TEXT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS learning_events (
            event_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
            event_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            document_id TEXT,
            payload_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(event_type, entity_id)
        );

        CREATE TABLE IF NOT EXISTS document_operations (
            operation_id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            operation_type TEXT NOT NULL,
            from_status TEXT NOT NULL,
            to_status TEXT NOT NULL,
            point_count_before INTEGER NOT NULL DEFAULT 0,
            point_count_after INTEGER,
            error_message TEXT,
            created_at TEXT NOT NULL,
            completed_at TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_turns_session_created
            ON conversation_turns(session_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_documents_status_updated
            ON documents(status, updated_at);
        CREATE INDEX IF NOT EXISTS idx_citations_document
            ON citations(document_id);
        CREATE INDEX IF NOT EXISTS idx_notes_session_created
            ON notes(session_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_notes_document
            ON notes(document_id);
        CREATE INDEX IF NOT EXISTS idx_events_session_created
            ON learning_events(session_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_events_type_created
            ON learning_events(event_type, created_at);
        """
        with self._lock:
            self._connection.executescript(schema)
            self._migrate_documents_schema_locked()
            self._migrate_citations_schema_locked()
            self._connection.commit()

    def _migrate_documents_schema_locked(self) -> None:
        columns = {
            row[1] for row in self._connection.execute("PRAGMA table_info(documents)")
        }
        additions = {
            "format": "TEXT NOT NULL DEFAULT 'pdf'",
            "content_hash": "TEXT",
            "embedding_model": "TEXT NOT NULL DEFAULT 'text-embedding-v4'",
            "embedding_dimension": "INTEGER NOT NULL DEFAULT 1024",
            "source_locator_scheme": "TEXT NOT NULL DEFAULT 'pdf-page-v1'",
            "source_unit_count": "INTEGER NOT NULL DEFAULT 0",
            "created_at": "TEXT",
        }
        for name, declaration in additions.items():
            if name not in columns:
                self._connection.execute(
                    f"ALTER TABLE documents ADD COLUMN {name} {declaration}"
                )
        self._connection.execute(
            "UPDATE documents SET content_hash = COALESCE(NULLIF(content_hash, ''), document_id), "
            "source_unit_count = CASE WHEN source_unit_count = 0 THEN pages_with_text ELSE source_unit_count END, "
            "created_at = COALESCE(created_at, updated_at)"
        )
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_documents_content_hash ON documents(content_hash)"
        )

    def _migrate_citations_schema_locked(self) -> None:
        """Allow Markdown citations to persist without fabricated page numbers."""
        columns = {
            row[1]: row for row in self._connection.execute("PRAGMA table_info(citations)")
        }
        page_start = columns.get("page_start")
        page_end = columns.get("page_end")
        if not page_start or not page_end or (page_start[3] == 0 and page_end[3] == 0):
            return

        self._connection.execute("ALTER TABLE citations RENAME TO citations_legacy")
        self._connection.execute(
            """
            CREATE TABLE citations (
                citation_row_id INTEGER PRIMARY KEY AUTOINCREMENT,
                turn_id TEXT NOT NULL REFERENCES conversation_turns(turn_id) ON DELETE CASCADE,
                citation_id TEXT NOT NULL,
                document_id TEXT NOT NULL,
                document_name TEXT NOT NULL,
                chunk_id TEXT NOT NULL,
                section TEXT NOT NULL,
                page_start INTEGER,
                page_end INTEGER,
                source_locator TEXT NOT NULL,
                score REAL NOT NULL,
                content TEXT NOT NULL,
                UNIQUE(turn_id, citation_id)
            )
            """
        )
        self._connection.execute(
            """
            INSERT INTO citations (
                citation_row_id, turn_id, citation_id, document_id, document_name,
                chunk_id, section, page_start, page_end, source_locator, score, content
            )
            SELECT
                citation_row_id, turn_id, citation_id, document_id, document_name,
                chunk_id, section, page_start, page_end, source_locator, score, content
            FROM citations_legacy
            """
        )
        self._connection.execute("DROP TABLE citations_legacy")
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_citations_document ON citations(document_id)"
        )

    @staticmethod
    def _document_from_row(row: sqlite3.Row) -> DocumentRecord:
        return DocumentRecord(
            row["document_id"],
            row["document_name"],
            row["source_path"],
            int(row["pages_with_text"]),
            int(row["chunk_count"]),
            int(row["indexed_point_count"]),
            row["status"],
            row["error_message"],
            row["updated_at"],
            row["format"],
            row["content_hash"] or row["document_id"],
            row["embedding_model"],
            int(row["embedding_dimension"]),
            row["source_locator_scheme"],
            int(row["source_unit_count"]),
            row["created_at"] or row["updated_at"],
        )

    def _require_session_locked(self, session_id: str) -> sqlite3.Row:
        row = self._connection.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if row is None:
            raise SessionNotFoundError(f"会话不存在: {session_id}")
        return row

    def _insert_event_locked(
        self,
        *,
        session_id: str,
        event_type: str,
        entity_id: str,
        document_id: str | None = None,
        payload: dict[str, Any] | None = None,
        created_at: str | None = None,
    ) -> None:
        self._connection.execute(
            """
            INSERT OR IGNORE INTO learning_events
            (event_id, session_id, event_type, entity_id, document_id, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                _new_id("event"),
                session_id,
                event_type,
                entity_id,
                document_id,
                json.dumps(payload or {}, ensure_ascii=False, sort_keys=True),
                created_at or _utc_now(),
            ),
        )

    def create_session(self, session_id: str | None = None) -> SessionRecord:
        session_id = session_id or _new_id("session")
        now = _utc_now()
        try:
            with self._lock:
                self._connection.execute(
                    "INSERT INTO sessions(session_id, created_at, updated_at) VALUES (?, ?, ?)",
                    (session_id, now, now),
                )
                self._insert_event_locked(
                    session_id=session_id,
                    event_type="session_created",
                    entity_id=session_id,
                    created_at=now,
                )
                self._connection.commit()
        except sqlite3.IntegrityError as exc:
            self._connection.rollback()
            raise DatabaseError(f"会话创建失败: {session_id}") from exc
        return SessionRecord(session_id, now, now)

    def upsert_document(
        self,
        *,
        document_id: str,
        document_name: str,
        source_path: str,
        pages_with_text: int = 0,
        chunk_count: int = 0,
        indexed_point_count: int = 0,
        status: str,
        error_message: str | None = None,
        format: str = "pdf",
        content_hash: str | None = None,
        embedding_model: str = "text-embedding-v4",
        embedding_dimension: int = 1024,
        source_locator_scheme: str = "pdf-page-v1",
        source_unit_count: int | None = None,
    ) -> DocumentRecord:
        if not document_id.strip() or not document_name.strip():
            raise NoteValidationError("文档 ID 和文档名不能为空")
        now = _utc_now()
        content_hash = content_hash or document_id
        source_unit_count = pages_with_text if source_unit_count is None else source_unit_count
        try:
            with self._lock:
                self._connection.execute(
                    """
                    INSERT INTO documents
                    (document_id, document_name, source_path, pages_with_text, chunk_count,
                     indexed_point_count, status, error_message, updated_at, format,
                     content_hash, embedding_model, embedding_dimension,
                     source_locator_scheme, source_unit_count, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(document_id) DO UPDATE SET
                      document_name=excluded.document_name,
                      source_path=excluded.source_path,
                      pages_with_text=excluded.pages_with_text,
                      chunk_count=excluded.chunk_count,
                      indexed_point_count=excluded.indexed_point_count,
                      status=excluded.status,
                      error_message=excluded.error_message,
                      updated_at=excluded.updated_at,
                      format=excluded.format,
                      content_hash=excluded.content_hash,
                      embedding_model=excluded.embedding_model,
                      embedding_dimension=excluded.embedding_dimension,
                      source_locator_scheme=excluded.source_locator_scheme,
                      source_unit_count=excluded.source_unit_count
                    """,
                    (
                        document_id,
                        document_name,
                        source_path,
                        pages_with_text,
                        chunk_count,
                        indexed_point_count,
                        status,
                        error_message,
                        now,
                        format,
                        content_hash,
                        embedding_model,
                        embedding_dimension,
                        source_locator_scheme,
                        source_unit_count,
                        now,
                    ),
                )
                row = self._connection.execute(
                    "SELECT * FROM documents WHERE document_id = ?", (document_id,)
                ).fetchone()
                self._connection.commit()
        except sqlite3.Error as exc:
            self._connection.rollback()
            raise DatabaseError(f"文档目录保存失败: {exc}") from exc
        assert row is not None
        return self._document_from_row(row)

    def list_documents(self) -> list[DocumentRecord]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT * FROM documents ORDER BY updated_at DESC"
            ).fetchall()
        return [self._document_from_row(row) for row in rows]

    def query_documents(
        self,
        *,
        search: str = "",
        format: str | None = None,
        status: str | None = None,
        sort: str = "updated_desc",
    ) -> list[DocumentRecord]:
        clauses: list[str] = []
        params: list[str] = []
        if search and search.strip():
            term = f"%{search.strip()}%"
            clauses.append("(document_name LIKE ? OR document_id LIKE ?)")
            params.extend([term, term])
        if format:
            clauses.append("format = ?")
            params.append(format)
        if status:
            clauses.append("status = ?")
            params.append(status)
        order = "updated_at DESC"
        if sort == "updated_asc":
            order = "updated_at ASC"
        elif sort == "name_asc":
            order = "document_name COLLATE NOCASE ASC, updated_at DESC"
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._lock:
            rows = self._connection.execute(
                f"SELECT * FROM documents{where} ORDER BY {order}", params
            ).fetchall()
        return [self._document_from_row(row) for row in rows]

    def get_document(self, document_id: str) -> DocumentRecord | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT * FROM documents WHERE document_id = ?", (document_id,)
            ).fetchone()
        return self._document_from_row(row) if row is not None else None

    def begin_document_operation(
        self,
        document_id: str,
        operation_type: str,
        to_status: str,
        point_count_before: int,
    ) -> str:
        operation_id = _new_id("docop")
        now = _utc_now()
        try:
            with self._lock:
                row = self._connection.execute(
                    "SELECT status FROM documents WHERE document_id = ?", (document_id,)
                ).fetchone()
                if row is None:
                    raise NoteValidationError(f"文档不存在: {document_id}")
                self._connection.execute(
                    "UPDATE documents SET status = ?, error_message = NULL, updated_at = ? WHERE document_id = ?",
                    (to_status, now, document_id),
                )
                self._connection.execute(
                    """INSERT INTO document_operations
                    (operation_id, document_id, operation_type, from_status, to_status,
                     point_count_before, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (operation_id, document_id, operation_type, row["status"], to_status, point_count_before, now),
                )
                self._connection.commit()
        except NoteValidationError:
            self._connection.rollback()
            raise
        except sqlite3.Error as exc:
            self._connection.rollback()
            raise DatabaseError(f"文档操作启动失败: {exc}") from exc
        return operation_id

    def finish_document_operation(
        self,
        operation_id: str,
        document_id: str,
        status: str,
        *,
        point_count_after: int | None = None,
        error_message: str | None = None,
    ) -> DocumentRecord:
        now = _utc_now()
        try:
            with self._lock:
                self._connection.execute(
                    "UPDATE documents SET status = ?, indexed_point_count = CASE WHEN ? = 'deleted' THEN 0 ELSE indexed_point_count END, error_message = ?, updated_at = ? WHERE document_id = ?",
                    (status, status, error_message, now, document_id),
                )
                changed = self._connection.execute(
                    "UPDATE document_operations SET to_status = ?, point_count_after = ?, error_message = ?, completed_at = ? WHERE operation_id = ?",
                    (status, point_count_after, error_message, now, operation_id),
                ).rowcount
                if changed != 1:
                    raise DatabaseError(f"文档操作不存在: {operation_id}")
                row = self._connection.execute(
                    "SELECT * FROM documents WHERE document_id = ?", (document_id,)
                ).fetchone()
                self._connection.commit()
        except DatabaseError:
            self._connection.rollback()
            raise
        except sqlite3.Error as exc:
            self._connection.rollback()
            raise DatabaseError(f"文档操作完成失败: {exc}") from exc
        if row is None:
            raise DatabaseError(f"文档不存在: {document_id}")
        return self._document_from_row(row)

    def list_document_operations(self, document_id: str | None = None) -> list[dict[str, Any]]:
        with self._lock:
            if document_id:
                rows = self._connection.execute(
                    "SELECT * FROM document_operations WHERE document_id = ? ORDER BY created_at",
                    (document_id,),
                ).fetchall()
            else:
                rows = self._connection.execute(
                    "SELECT * FROM document_operations ORDER BY created_at"
                ).fetchall()
        return [dict(row) for row in rows]

    def get_session(self, session_id: str) -> SessionRecord:
        with self._lock:
            row = self._require_session_locked(session_id)
        return SessionRecord(row["session_id"], row["created_at"], row["updated_at"])

    def recent_context(self, session_id: str, limit: int, max_chars: int) -> list[dict[str, str]]:
        if limit <= 0 or max_chars <= 0:
            return []
        with self._lock:
            self._require_session_locked(session_id)
            rows = self._connection.execute(
                """
                SELECT question, answer FROM conversation_turns
                WHERE session_id = ? ORDER BY turn_index DESC LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()
        selected_newest_first: list[dict[str, str]] = []
        used = 0
        for row in rows:
            item = {"question": row["question"], "answer": row["answer"]}
            item_size = len(item["question"]) + len(item["answer"])
            if selected_newest_first and used + item_size > max_chars:
                continue
            selected_newest_first.append(item)
            used += item_size
        return list(reversed(selected_newest_first))

    def context_history_candidates(
        self,
        session_id: str,
        *,
        limit: int,
        max_chars: int,
    ) -> list[ConversationContextCandidate]:
        """读取最近历史候选；至少保留最新一轮，最终预算由 Builder 收口。"""

        with self._lock:
            self._require_session_locked(session_id)
            if limit <= 0 or max_chars <= 0:
                return []
            rows = self._connection.execute(
                """
                SELECT turn_id, session_id, turn_index, question, answer, created_at
                FROM conversation_turns
                WHERE session_id = ?
                ORDER BY turn_index DESC
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()

        selected_newest_first: list[ConversationContextCandidate] = []
        used_chars = 0
        for row in rows:
            item_chars = len(row["question"]) + len(row["answer"])
            # 兼容原 recent_context：至少保留最近一轮候选；最终严格预算由
            # ContextBuilder 统一执行，避免短预算时完全失去指代上下文。
            if selected_newest_first and used_chars + item_chars > max_chars:
                continue
            selected_newest_first.append(
                ConversationContextCandidate(
                    turn_id=row["turn_id"],
                    session_id=row["session_id"],
                    turn_index=int(row["turn_index"]),
                    question=row["question"],
                    answer=row["answer"],
                    created_at=row["created_at"],
                )
            )
            used_chars += item_chars
        return list(reversed(selected_newest_first))

    def save_turn(self, session_id: str, response: AnswerResponse) -> ConversationTurn:
        now = _utc_now()
        turn_id = _new_id("turn")
        try:
            with self._lock:
                self._require_session_locked(session_id)
                next_index = int(
                    self._connection.execute(
                        "SELECT COALESCE(MAX(turn_index), 0) + 1 FROM conversation_turns WHERE session_id = ?",
                        (session_id,),
                    ).fetchone()[0]
                )
                self._connection.execute(
                    """
                    INSERT INTO conversation_turns
                    (turn_id, session_id, turn_index, question, answer, status, model, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        turn_id,
                        session_id,
                        next_index,
                        response.question,
                        response.answer,
                        response.status,
                        response.model,
                        now,
                    ),
                )
                for citation in response.citations:
                    self._insert_citation_locked(turn_id, citation)
                event_type = "answer_generated" if response.status == "answered" else "no_results"
                self._insert_event_locked(
                    session_id=session_id,
                    event_type="question_asked",
                    entity_id=turn_id,
                    created_at=now,
                )
                self._insert_event_locked(
                    session_id=session_id,
                    event_type=event_type,
                    entity_id=turn_id,
                    payload={"model": response.model, "status": response.status},
                    created_at=now,
                )
                self._connection.execute(
                    "UPDATE sessions SET updated_at = ? WHERE session_id = ?",
                    (now, session_id),
                )
                self._connection.commit()
        except sqlite3.Error as exc:
            self._connection.rollback()
            raise DatabaseError(f"问答记录保存失败: {exc}") from exc
        return ConversationTurn(
            turn_id=turn_id,
            session_id=session_id,
            turn_index=next_index,
            question=response.question,
            answer=response.answer,
            status=response.status,
            model=response.model,
            created_at=now,
            citations=list(response.citations),
        )

    def _insert_citation_locked(self, turn_id: str, citation: Citation) -> None:
        self._connection.execute(
            """
            INSERT INTO citations
            (turn_id, citation_id, document_id, document_name, chunk_id, section,
             page_start, page_end, source_locator, score, content)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                turn_id,
                citation.citation_id,
                citation.document_id,
                citation.document_name,
                citation.chunk_id,
                citation.section,
                citation.page_start,
                citation.page_end,
                citation.source_locator,
                citation.score,
                citation.content,
            ),
        )

    def _citation_from_row(self, row: sqlite3.Row) -> Citation:
        return Citation(
            citation_id=row["citation_id"],
            document_id=row["document_id"],
            document_name=row["document_name"],
            chunk_id=row["chunk_id"],
            section=row["section"],
            page_start=(
                int(row["page_start"])
                if row["page_start"] is not None
                else None
            ),
            page_end=(
                int(row["page_end"])
                if row["page_end"] is not None
                else None
            ),
            source_locator=row["source_locator"],
            score=float(row["score"]),
            content=row["content"],
        )

    def _citations_for_turn_locked(self, turn_id: str) -> list[Citation]:
        rows = self._connection.execute(
            "SELECT * FROM citations WHERE turn_id = ? ORDER BY citation_row_id", (turn_id,)
        ).fetchall()
        return [self._citation_from_row(row) for row in rows]

    def get_turn(self, turn_id: str) -> ConversationTurn:
        with self._lock:
            row = self._connection.execute(
                "SELECT * FROM conversation_turns WHERE turn_id = ?", (turn_id,)
            ).fetchone()
            if row is None:
                raise NoteValidationError(f"问答记录不存在: {turn_id}")
            citations = self._citations_for_turn_locked(turn_id)
        return ConversationTurn(
            turn_id=row["turn_id"],
            session_id=row["session_id"],
            turn_index=int(row["turn_index"]),
            question=row["question"],
            answer=row["answer"],
            status=row["status"],
            model=row["model"],
            created_at=row["created_at"],
            citations=citations,
        )

    def list_turns(self, session_id: str) -> list[ConversationTurn]:
        with self._lock:
            self._require_session_locked(session_id)
            rows = self._connection.execute(
                "SELECT turn_id FROM conversation_turns WHERE session_id = ? ORDER BY turn_index",
                (session_id,),
            ).fetchall()
        return [self.get_turn(row["turn_id"]) for row in rows]

    def create_note(
        self,
        *,
        session_id: str,
        content: str,
        turn_id: str | None = None,
        document_id: str | None = None,
        source_locator: str | None = None,
    ) -> NoteRecord:
        content = content.strip()
        if not content:
            raise NoteValidationError("笔记内容不能为空")
        now = _utc_now()
        note_id = _new_id("note")
        try:
            with self._lock:
                self._require_session_locked(session_id)
                source_rows = self._source_rows_for_note_locked(session_id, turn_id)
                source_docs = {row["document_id"] for row in source_rows}
                source_locators = {row["source_locator"] for row in source_rows}
                if turn_id and not source_rows:
                    raise NoteValidationError(f"问答记录不存在或不属于当前会话: {turn_id}")
                if document_id and document_id not in source_docs:
                    raise NoteValidationError("document_id 不存在于当前会话的来源记录中")
                if source_locator and source_locator not in source_locators:
                    raise NoteValidationError("source_locator 不存在于当前会话的来源记录中")
                if source_locator and not document_id:
                    document_id = next(
                        row["document_id"] for row in source_rows if row["source_locator"] == source_locator
                    )
                if document_id:
                    document = self._connection.execute(
                        "SELECT status FROM documents WHERE document_id = ?", (document_id,)
                    ).fetchone()
                    if document is not None and document["status"] in {"deleted", "deleting", "inconsistent"}:
                        raise NoteValidationError("已删除或正在恢复的文档不能新增笔记关联")
                self._connection.execute(
                    """
                    INSERT INTO notes
                    (note_id, session_id, turn_id, document_id, source_locator, content, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (note_id, session_id, turn_id, document_id, source_locator, content, now, now),
                )
                self._insert_event_locked(
                    session_id=session_id,
                    event_type="note_created",
                    entity_id=note_id,
                    document_id=document_id,
                    created_at=now,
                )
                self._connection.commit()
        except NoteValidationError:
            self._connection.rollback()
            raise
        except sqlite3.Error as exc:
            self._connection.rollback()
            raise DatabaseError(f"笔记保存失败: {exc}") from exc
        return NoteRecord(note_id, session_id, turn_id, document_id, source_locator, content, now, now)

    def _source_rows_for_note_locked(
        self, session_id: str, turn_id: str | None
    ) -> list[sqlite3.Row]:
        if turn_id:
            return self._connection.execute(
                """
                SELECT c.document_id, c.source_locator
                FROM citations c JOIN conversation_turns t ON t.turn_id = c.turn_id
                WHERE t.turn_id = ? AND t.session_id = ?
                """,
                (turn_id, session_id),
            ).fetchall()
        return self._connection.execute(
            """
            SELECT c.document_id, c.source_locator
            FROM citations c JOIN conversation_turns t ON t.turn_id = c.turn_id
            WHERE t.session_id = ?
            """,
            (session_id,),
        ).fetchall()

    def update_note(self, note_id: str, content: str) -> NoteRecord:
        content = content.strip()
        if not content:
            raise NoteValidationError("笔记内容不能为空")
        now = _utc_now()
        try:
            with self._lock:
                row = self._connection.execute(
                    "SELECT * FROM notes WHERE note_id = ?", (note_id,)
                ).fetchone()
                if row is None:
                    raise NoteNotFoundError(f"笔记不存在: {note_id}")
                self._connection.execute(
                    "UPDATE notes SET content = ?, updated_at = ? WHERE note_id = ?",
                    (content, now, note_id),
                )
                self._insert_event_locked(
                    session_id=row["session_id"],
                    event_type="note_updated",
                    entity_id=note_id,
                    document_id=row["document_id"],
                    created_at=now,
                )
                self._connection.commit()
        except (NoteNotFoundError, NoteValidationError):
            self._connection.rollback()
            raise
        except sqlite3.Error as exc:
            self._connection.rollback()
            raise DatabaseError(f"笔记更新失败: {exc}") from exc
        return NoteRecord(
            note_id=row["note_id"],
            session_id=row["session_id"],
            turn_id=row["turn_id"],
            document_id=row["document_id"],
            source_locator=row["source_locator"],
            content=content,
            created_at=row["created_at"],
            updated_at=now,
        )

    def list_notes(self, session_id: str | None = None) -> list[NoteRecord]:
        with self._lock:
            if session_id:
                self._require_session_locked(session_id)
                rows = self._connection.execute(
                    "SELECT * FROM notes WHERE session_id = ? ORDER BY created_at",
                    (session_id,),
                ).fetchall()
            else:
                rows = self._connection.execute("SELECT * FROM notes ORDER BY created_at").fetchall()
        return [self._note_from_row(row) for row in rows]

    def context_note_candidates(
        self,
        session_id: str,
        *,
        document_id: str | None,
        limit: int,
        max_chars: int,
    ) -> list[NoteRecord]:
        """读取当前会话和文档范围内的完整笔记候选，不修改持久状态。"""

        with self._lock:
            self._require_session_locked(session_id)
            if limit <= 0 or max_chars <= 0:
                return []
            if document_id is None:
                rows = self._connection.execute(
                    """
                    SELECT * FROM notes
                    WHERE session_id = ?
                    ORDER BY updated_at DESC, created_at DESC, note_id DESC
                    LIMIT ?
                    """,
                    (session_id, limit),
                ).fetchall()
            else:
                rows = self._connection.execute(
                    """
                    SELECT * FROM notes
                    WHERE session_id = ? AND (document_id IS NULL OR document_id = ?)
                    ORDER BY updated_at DESC, created_at DESC, note_id DESC
                    LIMIT ?
                    """,
                    (session_id, document_id, limit),
                ).fetchall()

        selected: list[NoteRecord] = []
        used_chars = 0
        for row in rows:
            item_chars = len(row["content"])
            if used_chars + item_chars > max_chars:
                continue
            selected.append(self._note_from_row(row))
            used_chars += item_chars
        return selected

    @staticmethod
    def _note_from_row(row: sqlite3.Row) -> NoteRecord:
        return NoteRecord(
            note_id=row["note_id"],
            session_id=row["session_id"],
            turn_id=row["turn_id"],
            document_id=row["document_id"],
            source_locator=row["source_locator"],
            content=row["content"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def stats(self, start_date: str | None = None, end_date: str | None = None) -> LearningStats:
        lower, upper = _date_bounds(start_date, end_date)
        with self._lock:
            session_count = self._count_locked("sessions", "created_at", lower, upper)
            question_count = self._count_locked("conversation_turns", "created_at", lower, upper)
            answered_count = self._count_locked(
                "conversation_turns", "created_at", lower, upper, "status = 'answered'"
            )
            no_results_count = self._count_locked(
                "conversation_turns", "created_at", lower, upper, "status = 'no_results'"
            )
            note_count = self._count_locked("notes", "created_at", lower, upper)
            documents = self._document_ids_locked(lower, upper)
            event_where, event_params = self._range_clause("created_at", lower, upper)
            daily_rows = self._connection.execute(
                f"""
                SELECT substr(created_at, 1, 10) AS day, event_type, COUNT(*) AS count
                FROM learning_events WHERE {event_where}
                GROUP BY day, event_type ORDER BY day, event_type
                """,
                event_params,
            ).fetchall()
        daily_events = [
            {"date": row["day"], "event_type": row["event_type"], "count": int(row["count"])}
            for row in daily_rows
        ]
        return LearningStats(
            period_start=start_date,
            period_end=end_date,
            session_count=session_count,
            question_count=question_count,
            answered_count=answered_count,
            no_results_count=no_results_count,
            note_count=note_count,
            document_count=len(documents),
            daily_events=daily_events,
        )

    def _count_locked(
        self,
        table: str,
        field: str,
        lower: str | None,
        upper: str | None,
        extra: str | None = None,
    ) -> int:
        where, params = self._range_clause(field, lower, upper, extra)
        return int(self._connection.execute(f"SELECT COUNT(*) FROM {table} WHERE {where}", params).fetchone()[0])

    @staticmethod
    def _range_clause(
        field: str, lower: str | None, upper: str | None, extra: str | None = None
    ) -> tuple[str, tuple[str, ...]]:
        clauses = [extra] if extra else []
        params: list[str] = []
        if lower:
            clauses.append(f"{field} >= ?")
            params.append(lower)
        if upper:
            clauses.append(f"{field} < ?")
            params.append(upper)
        return " AND ".join(clauses) if clauses else "1 = 1", tuple(params)

    def _document_ids_locked(self, lower: str | None, upper: str | None) -> set[str]:
        turn_where, turn_params = self._range_clause("t.created_at", lower, upper)
        note_where, note_params = self._range_clause("created_at", lower, upper)
        rows = self._connection.execute(
            f"""
            SELECT DISTINCT c.document_id FROM citations c
            JOIN conversation_turns t ON t.turn_id = c.turn_id
            WHERE {turn_where} AND c.document_id IS NOT NULL
            UNION
            SELECT DISTINCT document_id FROM notes
            WHERE {note_where} AND document_id IS NOT NULL
            """,
            turn_params + note_params,
        ).fetchall()
        return {row[0] for row in rows if row[0]}

    def report(
        self, start_date: str | None = None, end_date: str | None = None
    ) -> dict[str, Any]:
        stats = self.stats(start_date, end_date)
        return {
            "report_type": "learning_summary",
            "generated_at": _utc_now(),
            "scope": "SQLite persisted sessions, turns, citations, notes and learning events",
            "statistics": stats.as_dict(),
        }

    def integrity_check(self) -> str:
        try:
            with self._lock:
                result = self._connection.execute("PRAGMA integrity_check").fetchone()[0]
            return str(result)
        except sqlite3.Error as exc:
            raise DatabaseError(f"SQLite 完整性检查失败: {exc}") from exc

    def close(self) -> None:
        with self._lock:
            self._connection.close()

    def __enter__(self) -> "SQLiteMemoryStore":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()
