from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Callable

from pypdf import PdfReader

from .errors import DocumentExtractionError, DocumentNotFoundError
from .models import DocumentPage, DocumentSource, DocumentUnit, ParsedDocument, EMBEDDING_PROFILE


def document_id_for(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalise_text(text: str) -> str:
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def _section_from_text(text: str) -> str:
    for line in text.splitlines():
        candidate = line.strip()
        if re.match(r"^#{1,6}\s+", candidate):
            return re.sub(r"^#{1,6}\s+", "", candidate).strip()
        if re.match(r"^第.{1,12}[章节篇]\s*", candidate):
            return candidate[:120]
    return "未识别章节"


class PdfParser:
    def __init__(self, reader_factory: Callable[[str], PdfReader] = PdfReader):
        self._reader_factory = reader_factory

    def parse(self, path: str | Path) -> tuple[str, list[DocumentPage]]:
        source = Path(path)
        if not source.exists():
            raise DocumentNotFoundError(f"PDF 文件不存在: {source}")
        if not source.is_file():
            raise DocumentNotFoundError(f"PDF 路径不是文件: {source}")
        if source.suffix.lower() != ".pdf":
            raise DocumentExtractionError(f"仅支持 PDF 文件: {source.name}")

        try:
            reader = self._reader_factory(str(source))
            raw_pages = list(reader.pages)
        except Exception as exc:
            raise DocumentExtractionError(f"PDF 无法读取: {source.name}") from exc

        pages: list[DocumentPage] = []
        extraction_errors = 0
        for number, page in enumerate(raw_pages, start=1):
            try:
                text = _normalise_text(page.extract_text() or "")
            except Exception:
                extraction_errors += 1
                continue
            if text:
                pages.append(DocumentPage(number, text, _section_from_text(text)))

        if not pages:
            reason = "所有页面均无可提取文本"
            if extraction_errors:
                reason += f"，失败页面数: {extraction_errors}"
            raise DocumentExtractionError(f"PDF 文本提取失败: {source.name}；{reason}")
        return document_id_for(source), pages

    def parse_document(self, path: str | Path) -> ParsedDocument:
        source = Path(path)
        document_id, pages = self.parse(source)
        content_hash = document_id
        units = [
            DocumentUnit(
                content=page.text,
                section=page.section,
                section_path=page.section,
                paragraph_index=number,
                line_start=None,
                line_end=None,
                page_start=page.page_number,
                page_end=page.page_number,
            )
            for number, page in enumerate(pages, start=1)
        ]
        return ParsedDocument(
            source=DocumentSource(
                document_id=document_id,
                document_name=source.name,
                format="pdf",
                source_path=str(source),
                content_hash=content_hash,
                embedding_profile=EMBEDDING_PROFILE,
                source_locator_scheme="pdf-page-v1",
            ),
            units=units,
        )
