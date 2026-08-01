from __future__ import annotations

from pathlib import Path

import pytest
from pypdf import PdfWriter

from doc_qa.chunker import PageAwareChunker
from doc_qa.config import Settings
from doc_qa.errors import (
    DocumentExtractionError,
    DocumentNotFoundError,
    EmptyChunkError,
    EmbeddingApiError,
    EmbeddingServiceError,
    QdrantUnavailableError,
    VectorDimensionMismatch,
)
from doc_qa.ingestion import DocumentIngestionService
from doc_qa.models import DocumentPage
from doc_qa.pdf_parser import PdfParser
from doc_qa.qdrant_index import QdrantIndexer


class DeterministicEmbedding:
    model_name = "test-embedding-v4"
    dimension = 1024

    def encode(self, texts: list[str]) -> list[list[float]]:
        return [[float((index + 1) % 7) / 7 for _ in range(self.dimension)] for index, _ in enumerate(texts)]


class FailingEmbedding:
    model_name = "text-embedding-v4"
    dimension = 1024

    def encode(self, texts: list[str]) -> list[list[float]]:
        raise EmbeddingServiceError("test embedding failure")


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        embedding_model="test-embedding-v4",
        embedding_dimension=1024,
        embedding_batch_size=10,
        qdrant_local_path=tmp_path / "qdrant",
        chunk_size=180,
        chunk_overlap=20,
    )


def _service(tmp_path: Path, embedding=None) -> DocumentIngestionService:
    settings = _settings(tmp_path)
    return DocumentIngestionService(
        settings,
        embedding=embedding or DeterministicEmbedding(),
        indexer=QdrantIndexer(
            settings.collection_name,
            settings.embedding_dimension,
            local_path=settings.qdrant_local_path,
        ),
    )


def _write_pdf(path: Path, text: str | None = "# 测试章节\n\n这是用于索引验证的内容。") -> None:
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    if text:
        # pypdf cannot write text into a blank page without a font; use a small
        # hand-authored PDF fixture for parser tests below instead.
        pass
    with path.open("wb") as handle:
        writer.write(handle)


def _write_text_fixture(path: Path) -> None:
    # Minimal PDF with extractable text, generated as a stable test fixture.
    content = b"BT /F1 12 Tf 72 720 Td (Chapter 1) Tj 0 -20 Td (Indexable content.) Tj ET"
    objects = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n",
        b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
        b"5 0 obj << /Length " + str(len(content)).encode() + b" >> stream\n" + content + b"\nendstream endobj\n",
    ]
    header = b"%PDF-1.4\n"
    body = bytearray(header)
    offsets = [0]
    for obj in objects:
        offsets.append(len(body))
        body.extend(obj)
    xref = len(body)
    body.extend(b"xref\n0 6\n0000000000 65535 f \n")
    body.extend(b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:]))
    body.extend(b"trailer << /Size 6 /Root 1 0 R >>\nstartxref\n")
    body.extend(str(xref).encode() + b"\n%%EOF\n")
    path.write_bytes(body)


def test_missing_pdf_is_locatable(tmp_path: Path):
    with pytest.raises(DocumentNotFoundError, match="不存在"):
        PdfParser().parse(tmp_path / "missing.pdf")


def test_corrupted_pdf_is_reported(tmp_path: Path):
    path = tmp_path / "broken.pdf"
    path.write_bytes(b"not a pdf")
    with pytest.raises(DocumentExtractionError, match="无法读取"):
        PdfParser().parse(path)


def test_pdf_without_extractable_text_is_reported(tmp_path: Path):
    path = tmp_path / "empty.pdf"
    _write_pdf(path, text=None)
    with pytest.raises(DocumentExtractionError, match="文本提取失败"):
        PdfParser().parse(path)


def test_empty_chunks_are_filtered_and_all_empty_documents_fail():
    chunker = PageAwareChunker(chunk_size=50, overlap=5)
    chunks = chunker.chunk("doc", "test.pdf", "test.pdf", [DocumentPage(1, "  有内容  ", "章节")])
    assert len(chunks) == 1
    with pytest.raises(EmptyChunkError, match="非空分块"):
        chunker.chunk("doc", "test.pdf", "test.pdf", [DocumentPage(1, "   ", "章节")])


def test_real_baseline_pdf_parses_and_chunks():
    path = Path(__file__).parents[1] / "data" / "reference" / "Happy-LLM-0727.pdf"
    document_id, pages = PdfParser().parse(path)
    chunks = PageAwareChunker().chunk(document_id, path.name, path, pages)
    assert len(document_id) == 64
    assert len(pages) > 0
    assert len(chunks) > 0
    assert all(chunk.content.strip() for chunk in chunks)
    assert all(chunk.page_start >= 1 for chunk in chunks)


def test_duplicate_index_is_idempotent_and_metadata_is_complete(tmp_path: Path):
    pdf = tmp_path / "fixture.pdf"
    _write_text_fixture(pdf)
    service = _service(tmp_path)
    first = service.index_pdf(pdf)
    second = service.index_pdf(pdf)
    assert first.chunk_count == first.indexed_point_count
    assert second.chunk_count == second.indexed_point_count
    assert second.existing_chunk_count == second.chunk_count
    assert second.idempotent_replay is True
    assert second.metadata_complete is True


def test_embedding_failure_is_not_hidden(tmp_path: Path):
    pdf = tmp_path / "fixture.pdf"
    _write_text_fixture(pdf)
    with pytest.raises(EmbeddingServiceError):
        _service(tmp_path, FailingEmbedding()).index_pdf(pdf)


def test_qdrant_unavailable_is_reported():
    indexer = QdrantIndexer("unavailable", 1024, url="http://127.0.0.1:1", timeout=1)
    with pytest.raises(QdrantUnavailableError):
        indexer.ensure_collection()


def test_collection_dimension_mismatch_is_rejected(tmp_path: Path):
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams

    path = tmp_path / "qdrant"
    client = QdrantClient(path=str(path))
    client.create_collection("wrong", vectors_config=VectorParams(size=384, distance=Distance.COSINE))
    client.close()
    indexer = QdrantIndexer("wrong", 1024, local_path=path)
    with pytest.raises(VectorDimensionMismatch):
        indexer.ensure_collection()


def test_embedding_batch_size_rejects_provider_limit():
    from doc_qa.embedding import DashScopeEmbeddingProvider

    with pytest.raises(EmbeddingServiceError, match="最多支持 10 条文本"):
        DashScopeEmbeddingProvider(
            model_name="text-embedding-v4",
            expected_dimension=1024,
            api_key="test-key",
            base_url="https://example.invalid/v1",
            batch_size=11,
        )


def test_embedding_transient_error_is_retried(monkeypatch):
    from doc_qa.embedding import DashScopeEmbeddingProvider

    class RetryClient:
        dimension = 1024
        calls = 0

        def __init__(self, **kwargs):
            pass

        def encode(self, texts):
            if texts == "health_check":
                return [0.0] * 1024
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError('Embedding REST 调用失败: 503 {"code":"ModelServingError"}')
            return [[0.1] * 1024 for _ in texts]

    monkeypatch.setattr("hello_agents.memory.embedding.DashScopeEmbedding", RetryClient)
    monkeypatch.setattr("doc_qa.embedding.time.sleep", lambda _: None)
    provider = DashScopeEmbeddingProvider(
        model_name="text-embedding-v4",
        expected_dimension=1024,
        api_key="test-key",
        base_url="https://example.invalid/v1",
        batch_size=2,
        max_retries=2,
        retry_backoff_seconds=0,
    )

    vectors = provider.encode(["a", "b"])
    assert len(vectors) == 2
    assert provider._client.calls == 2


def test_embedding_error_preserves_http_details(monkeypatch):
    from doc_qa.embedding import DashScopeEmbeddingProvider

    class BadRequestClient:
        dimension = 1024

        def __init__(self, **kwargs):
            pass

        def encode(self, texts):
            raise RuntimeError(
                'Embedding REST 调用失败: 400 '
                '{"code":"InvalidParameter","message":"invalid input"}'
            )

    monkeypatch.setattr("hello_agents.memory.embedding.DashScopeEmbedding", BadRequestClient)
    provider = DashScopeEmbeddingProvider(
        model_name="text-embedding-v4",
        expected_dimension=1024,
        api_key="test-key",
        base_url="https://example.invalid/v1",
        max_retries=2,
        retry_backoff_seconds=0,
    )
    with pytest.raises(EmbeddingApiError, match="http_status=400.*provider_code=InvalidParameter"):
        provider.encode(["a"])
