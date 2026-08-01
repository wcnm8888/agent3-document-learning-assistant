from __future__ import annotations

import hashlib
from pathlib import Path

from .errors import EmptyChunkError
from .models import DocumentChunk, DocumentPage, ParsedDocument


def _cut_end(text: str, start: int, proposed_end: int) -> int:
    if proposed_end >= len(text):
        return len(text)
    minimum = start + max(1, int((proposed_end - start) * 0.6))
    for delimiter in ("\n", "。", "！", "？", ".", "!", "?", " "):
        position = text.rfind(delimiter, minimum, proposed_end)
        if position >= minimum:
            return position + 1
    return proposed_end


class PageAwareChunker:
    def __init__(self, chunk_size: int = 1200, overlap: int = 160):
        if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
            raise ValueError("chunk_size 必须大于 0，overlap 必须在 [0, chunk_size) 内")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(
        self,
        document_id: str,
        document_name: str,
        source_path: str | Path,
        pages: list[DocumentPage],
    ) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        for page in pages:
            text = page.text.strip()
            if not text:
                continue
            start = 0
            page_chunk_index = 0
            while start < len(text):
                end = _cut_end(text, start, min(len(text), start + self.chunk_size))
                content = text[start:end].strip()
                if content:
                    raw_id = f"{document_id}:{page.page_number}:{page_chunk_index}:{content}"
                    chunk_id = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()
                    chunks.append(
                        DocumentChunk(
                            document_id=document_id,
                            document_name=document_name,
                            chunk_id=chunk_id,
                            content=content,
                            page_start=page.page_number,
                            page_end=page.page_number,
                            section=page.section,
                            source_path=str(source_path),
                        )
                    )
                    page_chunk_index += 1
                if end >= len(text):
                    break
                next_start = max(start + 1, end - self.overlap)
                if next_start <= start:
                    raise EmptyChunkError(f"分块器无法推进: {document_name} 第 {page.page_number} 页")
                start = next_start

        if not chunks:
            raise EmptyChunkError(f"文档没有可建立索引的非空分块: {document_name}")
        return chunks

    def chunk_document(self, document: ParsedDocument) -> list[DocumentChunk]:
        """对统一解析结果分块；PDF 沿用旧算法以保持基线 chunk_id 不变。"""
        if document.source.format == "pdf":
            pages = [
                DocumentPage(unit.page_start or 0, unit.content, unit.section)
                for unit in document.units
                if unit.content.strip()
            ]
            return self.chunk(
                document.source.document_id,
                document.source.document_name,
                document.source.source_path,
                pages,
            )

        chunks: list[DocumentChunk] = []
        for unit in document.units:
            text = unit.content.strip()
            if not text:
                continue
            start = 0
            while start < len(text):
                end = _cut_end(text, start, min(len(text), start + self.chunk_size))
                content = text[start:end].strip()
                if content:
                    line_start = (unit.line_start or 1) + text[:start].count("\n")
                    line_end = line_start + max(0, content.count("\n"))
                    locator_without_chunk = (
                        f"section={unit.section_path}|paragraph={unit.paragraph_index}"
                        f"|lines={line_start}-{line_end}"
                    )
                    raw_id = (
                        f"{document.source.document_id}|{locator_without_chunk}|"
                        f"{content}|{document.source.embedding_profile}"
                    )
                    chunk_id = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()
                    chunks.append(
                        DocumentChunk(
                            document_id=document.source.document_id,
                            document_name=document.source.document_name,
                            chunk_id=chunk_id,
                            content=content,
                            page_start=None,
                            page_end=None,
                            section=unit.section,
                            source_path=document.source.source_path,
                            format="markdown",
                            content_hash=document.source.content_hash,
                            section_path=unit.section_path,
                            paragraph_index=unit.paragraph_index,
                            line_start=line_start,
                            line_end=line_end,
                            embedding_profile=document.source.embedding_profile,
                            source_locator_scheme=document.source.source_locator_scheme,
                        )
                    )
                if end >= len(text):
                    break
                next_start = max(start + 1, end - self.overlap)
                if next_start <= start:
                    raise EmptyChunkError(f"分块器无法推进: {document.source.document_name}")
                start = next_start

        if not chunks:
            raise EmptyChunkError(f"文档没有可建立索引的非空分块: {document.source.document_name}")
        return chunks
