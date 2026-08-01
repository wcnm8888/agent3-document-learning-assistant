from __future__ import annotations

from pathlib import Path

from .errors import DocumentExtractionError
from .markdown_parser import MarkdownParser
from .models import ParsedDocument
from .pdf_parser import PdfParser


class DocumentParser:
    """按扩展名选择 PDF 或 Markdown 解析器。"""

    def __init__(self, *, pdf_parser: PdfParser | None = None, markdown_parser: MarkdownParser | None = None):
        self.pdf_parser = pdf_parser or PdfParser()
        self.markdown_parser = markdown_parser or MarkdownParser()

    def parse(self, path: str | Path) -> ParsedDocument:
        source = Path(path)
        if source.suffix.lower() == ".pdf":
            return self.pdf_parser.parse_document(source)
        if source.suffix.lower() in {".md", ".markdown"}:
            return self.markdown_parser.parse(source)
        raise DocumentExtractionError(f"不支持的文档格式: {source.suffix or source.name}")
