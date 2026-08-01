from __future__ import annotations

from pathlib import Path

import pytest

from doc_qa.document_catalog import DocumentCatalogService
from doc_qa.config import Settings
from doc_qa.errors import NoteValidationError, QdrantUnavailableError
from doc_qa.lifecycle import DocumentLifecycleService
from doc_qa.memory_store import SQLiteMemoryStore
from doc_qa.models import DocumentChunk
from doc_qa.qdrant_index import QdrantIndexer
from doc_qa.ui import UIController


def _setup(tmp_path: Path) -> tuple[SQLiteMemoryStore, QdrantIndexer, DocumentLifecycleService]:
    store = SQLiteMemoryStore(tmp_path / "lifecycle.sqlite3")
    indexer = QdrantIndexer("lifecycle", 3, local_path=tmp_path / "qdrant")
    indexer.ensure_collection()
    chunk = DocumentChunk(
        document_id="doc-1", document_name="notes.md", chunk_id="chunk-1",
        content="内容", page_start=None, page_end=None, section="标题",
        source_path=str(tmp_path / "notes.md"), format="markdown",
        content_hash="hash-1", section_path="标题", paragraph_index=0,
        line_start=1, line_end=1, embedding_profile="text-embedding-v4:3",
        source_locator_scheme="markdown-heading-line-v1",
    )
    indexer.upsert([chunk], [[0.1, 0.2, 0.3]])
    store.upsert_document(
        document_id="doc-1", document_name="notes.md", source_path=chunk.source_path,
        chunk_count=1, indexed_point_count=1, status="indexed", format="markdown",
        content_hash="hash-1", embedding_dimension=3,
        source_locator_scheme="markdown-heading-line-v1", source_unit_count=1,
    )
    return store, indexer, DocumentLifecycleService(store, indexer)


def test_archive_keeps_points_and_unarchive_restores_visibility(tmp_path: Path) -> None:
    store, indexer, lifecycle = _setup(tmp_path)
    assert lifecycle.archive("doc-1").status == "archived"
    assert indexer.document_point_count("doc-1") == 1
    assert lifecycle.consistency("doc-1")[0]["ok"] is True
    assert lifecycle.unarchive("doc-1").status == "indexed"
    indexer.close(); store.close()


def test_delete_requires_confirmation_and_keeps_tombstone(tmp_path: Path) -> None:
    store, indexer, lifecycle = _setup(tmp_path)
    with pytest.raises(NoteValidationError, match="显式确认"):
        lifecycle.delete("doc-1")
    deleted = lifecycle.delete("doc-1", confirm=True)
    assert deleted.status == "deleted"
    assert indexer.document_point_count("doc-1") == 0
    assert store.get_document("doc-1") is not None
    assert lifecycle.consistency("doc-1")[0]["ok"] is True
    indexer.close(); store.close()


def test_qdrant_failure_restores_original_status(tmp_path: Path) -> None:
    store, indexer, lifecycle = _setup(tmp_path)

    def fail(_: str) -> int:
        raise QdrantUnavailableError("injected delete failure")

    indexer.delete_document_points = fail  # type: ignore[method-assign]
    with pytest.raises(QdrantUnavailableError):
        lifecycle.delete("doc-1", confirm=True)
    assert store.get_document("doc-1").status == "indexed"  # type: ignore[union-attr]
    assert store.list_document_operations("doc-1")[0]["to_status"] == "indexed"
    indexer.close(); store.close()


def test_deleted_document_cannot_receive_new_note_association(tmp_path: Path) -> None:
    store, indexer, lifecycle = _setup(tmp_path)
    session = store.create_session()
    lifecycle.delete("doc-1", confirm=True)
    with pytest.raises(NoteValidationError, match="document_id 不存在|不能新增笔记关联"):
        store.create_note(session_id=session.session_id, document_id="doc-1", content="历史")
    indexer.close(); store.close()


def test_restore_requires_existing_source_file_and_tombstone_is_preserved(tmp_path: Path) -> None:
    store, indexer, lifecycle = _setup(tmp_path)
    lifecycle.delete("doc-1", confirm=True)
    with pytest.raises(NoteValidationError, match="原始文件不存在"):
        lifecycle.restore_deleted("doc-1", reindex=lambda _: store.get_document("doc-1"))
    assert store.get_document("doc-1").status == "deleted"  # type: ignore[union-attr]
    indexer.close(); store.close()


def test_document_catalog_query_filters_and_details_are_format_aware(tmp_path: Path) -> None:
    controller = UIController(Settings(sqlite_path=tmp_path / "ui.sqlite3"))
    controller.store.upsert_document(
        document_id="pdf-1", document_name="Guide.pdf", source_path="Guide.pdf",
        pages_with_text=2, chunk_count=3, indexed_point_count=3, status="indexed",
    )
    controller.store.upsert_document(
        document_id="md-1", document_name="Notes.md", source_path="Notes.md",
        chunk_count=2, indexed_point_count=2, status="failed", format="markdown",
        error_message="Bearer secret-value", source_locator_scheme="markdown-heading-line-v1",
    )
    rows = controller.filter_documents("Notes", "MARKDOWN", "全部状态", "updated_desc")
    assert rows[0][0:4] == ["Notes.md", "MARKDOWN", "md-1", "failed"]
    assert "secret-value" not in rows[0][-1]
    detail = controller.document_details("md-1")
    assert detail["format"] == "markdown"
    assert detail["source_locator_scheme"] == "markdown-heading-line-v1"
    controller.close()
