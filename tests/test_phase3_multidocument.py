from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from doc_qa.config import Settings
from doc_qa.document_catalog import DocumentCatalogService
from doc_qa.document_scope import DocumentScopeState
from doc_qa.embedding import EmbeddingProvider
from doc_qa.errors import EmbeddingServiceError
from doc_qa.ingestion import DocumentIngestionService
from doc_qa.memory_store import SQLiteMemoryStore
from doc_qa.qdrant_index import QdrantIndexer


class RealProfileTestEmbedding:
    model_name = "text-embedding-v4"
    dimension = 1024

    def __init__(self) -> None:
        self.calls = 0

    def encode(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1
        return [[0.1] * self.dimension for _ in texts]


class FailingProfileTestEmbedding(RealProfileTestEmbedding):
    def encode(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1
        raise EmbeddingServiceError("Embedding API 失败（测试注入）")


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        embedding_model="text-embedding-v4",
        embedding_dimension=1024,
        qdrant_local_path=tmp_path / "qdrant",
        collection_prefix="phase3",
        chunk_size=120,
        chunk_overlap=10,
    )


def _service(tmp_path: Path, embedding: EmbeddingProvider, store: SQLiteMemoryStore):
    settings = _settings(tmp_path)
    indexer = QdrantIndexer(
        settings.collection_name,
        settings.embedding_dimension,
        local_path=settings.qdrant_local_path,
    )
    return (
        DocumentIngestionService(
            settings,
            embedding=embedding,
            indexer=indexer,
            catalog=DocumentCatalogService(store),
        ),
        indexer,
    )


def test_markdown_real_profile_index_is_idempotent_and_cataloged(tmp_path: Path) -> None:
    markdown = tmp_path / "学习材料.md"
    markdown.write_text(
        "# 文档标题\n\n这是第一段中文内容。\n\n## 第二节\n\n这是第二段内容。",
        encoding="utf-8",
    )
    store = SQLiteMemoryStore(tmp_path / "docqa.sqlite3")
    embedding = RealProfileTestEmbedding()
    service, indexer = _service(tmp_path, embedding, store)

    first = service.index_document(markdown)
    second = service.index_document(markdown)

    assert first.status == "indexed"
    assert first.embedding_model == "text-embedding-v4"
    assert first.embedding_dimension == 1024
    assert first.chunk_count > 0
    assert first.existing_chunk_count == 0
    assert first.metadata_complete is True
    assert second.status == "duplicate"
    assert second.idempotent_replay is True
    assert second.existing_chunk_count == second.chunk_count
    assert embedding.calls == 1
    assert indexer.document_point_count(first.document_id) == first.chunk_count
    record = store.get_document(first.document_id)
    assert record is not None
    assert record.format == "markdown"
    assert record.status == "indexed"
    assert record.indexed_point_count == first.chunk_count

    hits = indexer.search([0.1] * 1024, limit=20, document_id=first.document_id, score_threshold=0)
    assert hits
    assert all(hit.payload["document_id"] == first.document_id for hit in hits)
    assert all(hit.payload["format"] == "markdown" for hit in hits)
    assert all(hit.payload["page_start"] is None for hit in hits)
    assert all("lines=" in str(hit.payload["source_locator"]) for hit in hits)
    service.close()
    store.close()


def test_same_name_different_content_isolated_and_all_scope_preserves_ids(tmp_path: Path) -> None:
    first_path = tmp_path / "one" / "notes.md"
    second_path = tmp_path / "two" / "notes.md"
    first_path.parent.mkdir()
    second_path.parent.mkdir()
    first_path.write_text("# 文档一\n\n苹果知识。", encoding="utf-8")
    second_path.write_text("# 文档二\n\n香蕉知识。", encoding="utf-8")
    store = SQLiteMemoryStore(tmp_path / "docqa.sqlite3")
    service, indexer = _service(tmp_path, RealProfileTestEmbedding(), store)

    first = service.index_document(first_path)
    second = service.index_document(second_path)
    first_hits = indexer.search([0.1] * 1024, limit=20, document_id=first.document_id, score_threshold=0)
    second_hits = indexer.search([0.1] * 1024, limit=20, document_id=second.document_id, score_threshold=0)
    all_hits = indexer.search([0.1] * 1024, limit=20, score_threshold=0)

    assert first.document_id != second.document_id
    assert first_hits and second_hits
    assert {hit.payload["document_id"] for hit in first_hits} == {first.document_id}
    assert {hit.payload["document_id"] for hit in second_hits} == {second.document_id}
    assert {hit.payload["document_id"] for hit in all_hits} == {first.document_id, second.document_id}
    assert indexer.point_count() == first.chunk_count + second.chunk_count
    service.close()
    store.close()


def test_failed_new_markdown_does_not_change_existing_points(tmp_path: Path) -> None:
    good = tmp_path / "good.md"
    bad = tmp_path / "bad.md"
    good.write_text("# 已有文档\n\n已有内容。", encoding="utf-8")
    bad.write_text("# 新文档\n\n新内容。", encoding="utf-8")
    store = SQLiteMemoryStore(tmp_path / "docqa.sqlite3")
    good_service, indexer = _service(tmp_path, RealProfileTestEmbedding(), store)
    good_report = good_service.index_document(good)
    before = indexer.point_count()

    settings = _settings(tmp_path)
    failing_service = DocumentIngestionService(
        settings,
        embedding=FailingProfileTestEmbedding(),
        indexer=indexer,
        catalog=DocumentCatalogService(store),
    )
    with pytest.raises(EmbeddingServiceError, match="测试注入"):
        failing_service.index_document(bad)

    assert indexer.point_count() == before
    assert indexer.document_point_count(good_report.document_id) == good_report.chunk_count
    bad_record = store.get_document(hashlib.sha256(bad.read_bytes()).hexdigest())
    assert bad_record is not None
    assert bad_record.status == "failed"
    good_service.close()
    store.close()


def test_switching_document_scope_clears_temporary_state() -> None:
    previous = DocumentScopeState(
        document_id="doc-a",
        conversation_context=({"question": "旧问题", "answer": "旧回答"},),
        citations=({"document_id": "doc-a", "source_locator": "a#lines=1-2"},),
        pending_note="旧笔记",
    )
    switched = previous.switch("doc-b")
    all_documents = switched.all_documents()

    assert switched.document_id == "doc-b"
    assert switched.conversation_context == ()
    assert switched.citations == ()
    assert switched.pending_note == ""
    assert all_documents.document_id is None
