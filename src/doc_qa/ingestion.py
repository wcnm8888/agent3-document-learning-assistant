from __future__ import annotations

from pathlib import Path

from .chunker import PageAwareChunker
from .config import Settings
from .document_parser import DocumentParser
from .document_catalog import DocumentCatalogService
from .embedding import EmbeddingProvider
from .errors import EmbeddingDimensionMismatch, EmbeddingServiceError
from .models import DocumentChunk, IndexReport, ParsedDocument
from .pdf_parser import PdfParser
from .qdrant_index import QdrantIndexer


class DocumentIngestionService:
    def __init__(
        self,
        settings: Settings,
        *,
        parser: PdfParser | None = None,
        chunker: PageAwareChunker | None = None,
        embedding: EmbeddingProvider,
        indexer: QdrantIndexer | None = None,
        catalog: DocumentCatalogService | None = None,
    ):
        self.settings = settings
        self.parser = parser or PdfParser()
        self.document_parser = DocumentParser(pdf_parser=self.parser)
        self.chunker = chunker or PageAwareChunker(settings.chunk_size, settings.chunk_overlap)
        self.embedding = embedding
        self.catalog = catalog
        self.indexer = indexer or QdrantIndexer(
            settings.collection_name,
            settings.embedding_dimension,
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            local_path=settings.qdrant_local_path,
            timeout=settings.qdrant_timeout,
        )

    def parse_document(self, path: str | Path) -> ParsedDocument:
        """执行格式感知解析，不调用 Embedding、Qdrant 或外部服务。"""
        return self.document_parser.parse(path)

    def parse_and_chunk(self, path: str | Path) -> tuple[ParsedDocument, list[DocumentChunk]]:
        document = self.parse_document(path)
        return document, self.chunker.chunk_document(document)

    def index_pdf(self, path: str | Path) -> IndexReport:
        """保持 Phase 2 的 PDF 入口兼容，内部统一走格式感知索引。"""
        source = Path(path)
        if source.suffix.lower() != ".pdf":
            raise ValueError(f"index_pdf 仅支持 PDF 文件: {source.name}")
        return self.index_document(source)

    def index_document(self, path: str | Path) -> IndexReport:
        """执行 PDF/Markdown 的解析、分块、真实 Embedding 和 Qdrant 幂等索引。"""
        source = Path(path)
        document: ParsedDocument | None = None
        chunks: list[DocumentChunk] = []
        catalog_registered = False
        try:
            document, chunks = self.parse_and_chunk(source)
            if self.embedding.model_name != self.settings.embedding_model:
                raise EmbeddingServiceError(
                    f"Embedding 模型为 {self.embedding.model_name}，期望 {self.settings.embedding_model}"
                )
            if self.embedding.dimension != self.settings.embedding_dimension:
                raise EmbeddingDimensionMismatch(
                    f"Embedding 维度为 {self.embedding.dimension}，期望 {self.settings.embedding_dimension}"
                )

            if self.catalog is not None:
                self.catalog.register(
                    document.source,
                    source_unit_count=len(document.units),
                    chunk_count=len(chunks),
                    status="validating",
                )
                catalog_registered = True
                self.catalog.update_status(document.source.document_id, "parsing")

            self.indexer.ensure_collection()
            chunk_ids = {chunk.chunk_id for chunk in chunks}
            existing_ids = self.indexer.existing_chunk_ids(chunk_ids)
            missing_chunks = [chunk for chunk in chunks if chunk.chunk_id not in existing_ids]

            if self.catalog is not None:
                self.catalog.update_status(document.source.document_id, "indexing")
            if missing_chunks:
                vectors = self.embedding.encode([chunk.content for chunk in missing_chunks])
                self.indexer.upsert(missing_chunks, vectors)

            indexed_count = self.indexer.point_count()
            document_point_count = self.indexer.document_point_count(document.source.document_id)
            metadata_repaired_count = self.indexer.ensure_metadata(chunks)
            metadata_complete = self.indexer.verify_metadata(chunk_ids)
            if not metadata_complete:
                raise RuntimeError("Qdrant 索引元数据完整性验证失败")

            replay = len(existing_ids) == len(chunks)
            status = "duplicate" if replay else "indexed"
            if self.catalog is not None:
                self.catalog.mark_indexed(
                    document.source,
                    pages_with_text=sum(unit.page_start is not None for unit in document.units),
                    source_unit_count=len(document.units),
                    chunk_count=len(chunks),
                    indexed_point_count=document_point_count,
                )
            return IndexReport(
                status=status,
                document_id=document.source.document_id,
                document_name=document.source.document_name,
                collection_name=self.settings.collection_name,
                embedding_model=self.embedding.model_name,
                embedding_dimension=self.embedding.dimension,
                pages_with_text=sum(unit.page_start is not None for unit in document.units),
                chunk_count=len(chunks),
                existing_chunk_count=len(existing_ids),
                indexed_point_count=indexed_count,
                metadata_complete=metadata_complete,
                idempotent_replay=replay,
                source_path=document.source.source_path,
                metadata_repaired_count=metadata_repaired_count,
            )
        except Exception as exc:
            if self.catalog is not None and document is not None and catalog_registered:
                try:
                    self.catalog.update_status(
                        document.source.document_id,
                        "failed",
                        error_message=str(exc),
                    )
                except Exception:
                    pass
            raise

    def close(self) -> None:
        self.indexer.close()
