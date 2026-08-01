from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from .document_catalog import DocumentCatalogService
from .errors import NoteValidationError
from .memory_store import DocumentRecord, SQLiteMemoryStore
from .qdrant_index import QdrantIndexer


class DocumentLifecycleService:
    """文档归档、删除和恢复边界；不直接删除 SQLite tombstone。"""

    def __init__(self, store: SQLiteMemoryStore, indexer: QdrantIndexer):
        self.store = store
        self.indexer = indexer
        self.catalog = DocumentCatalogService(store)

    def archive(self, document_id: str) -> DocumentRecord:
        record = self._require(document_id)
        if record.status != "indexed":
            raise NoteValidationError(f"只有 indexed 文档可以归档: {record.status}")
        return self.catalog.update_status(document_id, "archived")

    def unarchive(self, document_id: str) -> DocumentRecord:
        record = self._require(document_id)
        if record.status != "archived":
            raise NoteValidationError(f"只有 archived 文档可以恢复: {record.status}")
        return self.catalog.update_status(document_id, "indexed")

    def delete(self, document_id: str, *, confirm: bool = False) -> DocumentRecord:
        if not confirm:
            raise NoteValidationError("删除文档必须显式确认")
        record = self._require(document_id)
        if record.status not in {"indexed", "archived"}:
            raise NoteValidationError(f"当前状态不允许删除: {record.status}")
        before = self.indexer.document_point_count(document_id)
        operation_id = self.store.begin_document_operation(document_id, "delete", "deleting", before)
        try:
            self.indexer.delete_document_points(document_id)
            after = self.indexer.document_point_count(document_id)
            if after != 0:
                raise RuntimeError(f"删除后 points 仍为 {after}")
            return self.store.finish_document_operation(
                operation_id, document_id, "deleted", point_count_after=after
            )
        except Exception as exc:
            current = self.store.get_document(document_id)
            fallback = record.status if current and current.status == "deleting" else "inconsistent"
            try:
                remaining = self.indexer.document_point_count(document_id)
            except Exception:
                remaining = None
            self.store.finish_document_operation(
                operation_id, document_id, fallback,
                point_count_after=remaining,
                error_message=str(exc),
            )
            raise

    def restore_deleted(
        self, document_id: str, *, reindex: Callable[[Path], DocumentRecord]
    ) -> DocumentRecord:
        record = self._require(document_id)
        if record.status != "deleted":
            raise NoteValidationError(f"只有 deleted tombstone 可以恢复: {record.status}")
        source = Path(record.source_path)
        if not source.is_file():
            raise NoteValidationError(f"原始文件不存在，无法恢复: {source}")
        self.catalog.update_status(document_id, "restoring")
        try:
            restored = reindex(source)
            if restored.document_id != document_id:
                raise NoteValidationError("恢复后的 document_id 与 tombstone 不一致")
            return restored
        except Exception as exc:
            self.catalog.update_status(document_id, "deleted", error_message=str(exc))
            raise

    def consistency(self, document_id: str | None = None) -> list[dict[str, object]]:
        records = [self._require(document_id)] if document_id else self.store.list_documents()
        results: list[dict[str, object]] = []
        for record in records:
            points = self.indexer.document_point_count(record.document_id)
            if record.status == "deleted":
                ok = points == 0
            elif record.status in {"indexed", "archived"}:
                ok = points == record.indexed_point_count
            else:
                ok = False
            results.append({"document_id": record.document_id, "status": record.status, "points": points, "expected": record.indexed_point_count, "ok": ok})
        return results

    def _require(self, document_id: str) -> DocumentRecord:
        record = self.store.get_document(document_id)
        if record is None:
            raise NoteValidationError(f"文档不存在: {document_id}")
        return record
