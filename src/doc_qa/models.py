from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote


EMBEDDING_PROFILE = "text-embedding-v4:1024"


@dataclass(frozen=True)
class DocumentSource:
    document_id: str
    document_name: str
    format: str
    source_path: str
    content_hash: str
    embedding_profile: str = EMBEDDING_PROFILE
    source_locator_scheme: str = "pdf-page-v1"


@dataclass(frozen=True)
class DocumentUnit:
    content: str
    section: str
    section_path: str
    paragraph_index: int
    line_start: int | None
    line_end: int | None
    page_start: int | None
    page_end: int | None


@dataclass(frozen=True)
class ParsedDocument:
    source: DocumentSource
    units: list[DocumentUnit]


@dataclass(frozen=True)
class DocumentPage:
    page_number: int
    text: str
    section: str


@dataclass(frozen=True)
class DocumentChunk:
    document_id: str
    document_name: str
    chunk_id: str
    content: str
    page_start: int | None
    page_end: int | None
    section: str
    source_path: str
    format: str = "pdf"
    content_hash: str | None = None
    section_path: str = ""
    paragraph_index: int | None = None
    line_start: int | None = None
    line_end: int | None = None
    embedding_profile: str = EMBEDDING_PROFILE
    source_locator_scheme: str = "pdf-page-v1"

    def source_locator(self) -> str:
        if self.format == "markdown":
            section_path = quote(self.section_path or self.section or "根文档", safe="")
            paragraph = self.paragraph_index if self.paragraph_index is not None else 0
            line_start = self.line_start if self.line_start is not None else 0
            line_end = self.line_end if self.line_end is not None else line_start
            return (
                f"{self.document_name}#section={section_path}&paragraph={paragraph}"
                f"&lines={line_start}-{line_end}&chunk={self.chunk_id}"
            )
        return f"{self.document_name}#page={self.page_start}&chunk={self.chunk_id}"

    def payload(self) -> dict[str, object]:
        return {
            "document_id": self.document_id,
            "document_name": self.document_name,
            "chunk_id": self.chunk_id,
            "content": self.content,
            "page_start": self.page_start,
            "page_end": self.page_end,
            "section": self.section,
            "source_path": self.source_path,
            "format": self.format,
            "content_hash": self.content_hash or self.document_id,
            "section_path": self.section_path or self.section,
            "paragraph_index": self.paragraph_index,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "embedding_profile": self.embedding_profile,
            "source_locator_scheme": self.source_locator_scheme,
            "source_locator": self.source_locator(),
        }


@dataclass(frozen=True)
class IndexReport:
    status: str
    document_id: str
    document_name: str
    collection_name: str
    embedding_model: str
    embedding_dimension: int
    pages_with_text: int
    chunk_count: int
    existing_chunk_count: int
    indexed_point_count: int
    metadata_complete: bool
    idempotent_replay: bool
    source_path: str
    metadata_repaired_count: int = 0

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "document_id": self.document_id,
            "document_name": self.document_name,
            "collection_name": self.collection_name,
            "embedding_model": self.embedding_model,
            "embedding_dimension": self.embedding_dimension,
            "pages_with_text": self.pages_with_text,
            "chunk_count": self.chunk_count,
            "existing_chunk_count": self.existing_chunk_count,
            "indexed_point_count": self.indexed_point_count,
            "metadata_complete": self.metadata_complete,
            "idempotent_replay": self.idempotent_replay,
            "source_path": self.source_path,
            "metadata_repaired_count": self.metadata_repaired_count,
        }


@dataclass(frozen=True)
class RetrievalHit:
    point_id: str
    score: float
    payload: dict[str, object]


@dataclass(frozen=True)
class Citation:
    citation_id: str
    document_id: str
    document_name: str
    chunk_id: str
    section: str
    page_start: int | None
    page_end: int | None
    source_locator: str
    score: float
    content: str

    def as_dict(self) -> dict[str, object]:
        return {
            "citation_id": self.citation_id,
            "document_id": self.document_id,
            "document_name": self.document_name,
            "chunk_id": self.chunk_id,
            "section": self.section,
            "page_start": self.page_start,
            "page_end": self.page_end,
            "source_locator": self.source_locator,
            "score": self.score,
            "content": self.content,
        }


@dataclass(frozen=True)
class AnswerResponse:
    status: str
    question: str
    answer: str
    citations: list[Citation]
    retrieved_count: int
    model: str

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "question": self.question,
            "answer": self.answer,
            "citations": [citation.as_dict() for citation in self.citations],
            "retrieved_count": self.retrieved_count,
            "model": self.model,
        }
