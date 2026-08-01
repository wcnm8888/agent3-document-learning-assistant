from __future__ import annotations

from dataclasses import dataclass

from .errors import NoteValidationError
from .memory_store import DocumentRecord, SQLiteMemoryStore
from .models import DocumentSource


CANONICAL_STATUSES = {
    "pending",
    "validating",
    "parsing",
    "indexing",
    "indexed",
    "failed",
    "archived",
    "deleting",
    "deleted",
    "restoring",
    "inconsistent",
}


@dataclass(frozen=True)
class CatalogResult:
    document: DocumentRecord
    outcome: str


class DocumentCatalogService:
    """SQLite 文档目录边界；duplicate 是操作结果，不是持久化状态。"""

    def __init__(self, store: SQLiteMemoryStore):
        self.store = store

    def register(
        self,
        source: DocumentSource,
        *,
        source_unit_count: int = 0,
        chunk_count: int = 0,
        status: str = "pending",
        error_message: str | None = None,
    ) -> CatalogResult:
        if status not in CANONICAL_STATUSES:
            raise NoteValidationError(f"不支持的文档状态: {status}")
        existing = self.store.get_document(source.document_id)
        if existing is not None and existing.content_hash == source.content_hash:
            return CatalogResult(existing, "duplicate")
        if existing is not None and existing.content_hash != source.content_hash:
            raise NoteValidationError(
                f"document_id 与 content_hash 冲突，拒绝覆盖目录记录: {source.document_id}"
            )
        record = self.store.upsert_document(
            document_id=source.document_id,
            document_name=source.document_name,
            source_path=source.source_path,
            pages_with_text=0,
            chunk_count=chunk_count,
            indexed_point_count=0,
            status=status,
            error_message=error_message,
            format=source.format,
            content_hash=source.content_hash,
            embedding_model=source.embedding_profile.split(":", 1)[0],
            embedding_dimension=int(source.embedding_profile.rsplit(":", 1)[1]),
            source_locator_scheme=source.source_locator_scheme,
            source_unit_count=source_unit_count,
        )
        return CatalogResult(record, "created" if existing is None else "updated")

    def update_status(
        self,
        document_id: str,
        status: str,
        *,
        error_message: str | None = None,
    ) -> DocumentRecord:
        if status not in CANONICAL_STATUSES:
            raise NoteValidationError(f"不支持的文档状态: {status}")
        existing = self.store.get_document(document_id)
        if existing is None:
            raise NoteValidationError(f"文档不存在: {document_id}")
        return self.store.upsert_document(
            document_id=existing.document_id,
            document_name=existing.document_name,
            source_path=existing.source_path,
            pages_with_text=existing.pages_with_text,
            chunk_count=existing.chunk_count,
            indexed_point_count=existing.indexed_point_count,
            status=status,
            error_message=error_message,
            format=existing.format,
            content_hash=existing.content_hash,
            embedding_model=existing.embedding_model,
            embedding_dimension=existing.embedding_dimension,
            source_locator_scheme=existing.source_locator_scheme,
            source_unit_count=existing.source_unit_count,
        )

    def mark_indexed(
        self,
        source: DocumentSource,
        *,
        pages_with_text: int,
        source_unit_count: int,
        chunk_count: int,
        indexed_point_count: int,
    ) -> DocumentRecord:
        """在 Qdrant 校验完成后提交 canonical indexed 状态。"""
        return self.store.upsert_document(
            document_id=source.document_id,
            document_name=source.document_name,
            source_path=source.source_path,
            pages_with_text=pages_with_text,
            chunk_count=chunk_count,
            indexed_point_count=indexed_point_count,
            status="indexed",
            format=source.format,
            content_hash=source.content_hash,
            embedding_model=source.embedding_profile.split(":", 1)[0],
            embedding_dimension=int(source.embedding_profile.rsplit(":", 1)[1]),
            source_locator_scheme=source.source_locator_scheme,
            source_unit_count=source_unit_count,
        )
