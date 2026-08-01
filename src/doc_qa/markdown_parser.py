from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .errors import DocumentExtractionError, DocumentNotFoundError
from .models import DocumentSource, DocumentUnit, ParsedDocument


_ATX_HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
_SETEXT = re.compile(r"^\s*(=+|-+)\s*$")
_FENCE = re.compile(r"^\s{0,3}(```|~~~)")
_LIST = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
_TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{1,}:?\s*(?:\|\s*:?-{1,}:?\s*)+\|?\s*$")


def _content_hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _is_table_start(lines: list[str], index: int) -> bool:
    return (
        index + 1 < len(lines)
        and "|" in lines[index]
        and bool(_TABLE_SEPARATOR.match(lines[index + 1]))
    )


def _is_block_start(lines: list[str], index: int, in_code: bool = False) -> bool:
    if in_code or not lines[index].strip():
        return True
    if _ATX_HEADING.match(lines[index]) or _FENCE.match(lines[index]):
        return True
    if _LIST.match(lines[index]) or _is_table_start(lines, index):
        return True
    return index + 1 < len(lines) and _SETEXT.match(lines[index + 1]) is not None


class MarkdownParser:
    """将 Markdown 解析为带原始行号的非执行文档单元。"""

    def parse(self, path: str | Path) -> ParsedDocument:
        source = Path(path)
        if not source.exists() or not source.is_file():
            raise DocumentNotFoundError(f"Markdown 文件不存在: {source}")
        if source.suffix.lower() not in {".md", ".markdown"}:
            raise DocumentExtractionError(f"仅支持 .md 或 .markdown 文件: {source.name}")

        raw = source.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise DocumentExtractionError(
                f"Markdown 不是有效 UTF-8: {source.name}, 字节位置 {exc.start}"
            ) from exc

        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        units: list[DocumentUnit] = []
        heading_stack: list[str] = []
        paragraph_index = 0
        index = 0

        def current_section() -> tuple[str, str]:
            return (heading_stack[-1] if heading_stack else "根文档", " / ".join(heading_stack) or "根文档")

        def add_unit(start: int, end: int) -> None:
            nonlocal paragraph_index
            content = "\n".join(lines[start - 1 : end]).strip()
            if not content:
                return
            section, section_path = current_section()
            paragraph_index += 1
            units.append(
                DocumentUnit(
                    content=content,
                    section=section,
                    section_path=section_path,
                    paragraph_index=paragraph_index,
                    line_start=start,
                    line_end=end,
                    page_start=None,
                    page_end=None,
                )
            )

        while index < len(lines):
            line = lines[index]
            line_number = index + 1
            if not line.strip():
                index += 1
                continue

            atx = _ATX_HEADING.match(line)
            if atx:
                level = len(atx.group(1))
                title = atx.group(2).strip()
                heading_stack = heading_stack[: level - 1] + [title]
                index += 1
                continue

            if (
                index + 1 < len(lines)
                and line.strip()
                and _SETEXT.match(lines[index + 1])
                and not _FENCE.match(line)
            ):
                level = 1 if lines[index + 1].lstrip().startswith("=") else 2
                title = line.strip()
                heading_stack = heading_stack[: level - 1] + [title]
                index += 2
                continue

            fence = _FENCE.match(line)
            if fence:
                marker = fence.group(1)[0]
                end_index = index + 1
                while end_index < len(lines) and not re.match(
                    rf"^\s{{0,3}}{re.escape(marker)}{{3,}}", lines[end_index]
                ):
                    end_index += 1
                if end_index < len(lines):
                    end_index += 1
                add_unit(line_number, end_index)
                index = end_index
                continue

            if _is_table_start(lines, index):
                end_index = index + 2
                while end_index < len(lines) and lines[end_index].strip() and "|" in lines[end_index]:
                    end_index += 1
                add_unit(line_number, end_index)
                index = end_index
                continue

            if _LIST.match(line):
                end_index = index + 1
                while end_index < len(lines):
                    candidate = lines[end_index]
                    if not candidate.strip() or _ATX_HEADING.match(candidate) or _FENCE.match(candidate):
                        break
                    if _LIST.match(candidate) or candidate.startswith((" ", "\t")):
                        end_index += 1
                        continue
                    break
                add_unit(line_number, end_index)
                index = end_index
                continue

            end_index = index + 1
            while end_index < len(lines) and lines[end_index].strip():
                if _is_block_start(lines, end_index):
                    break
                end_index += 1
            add_unit(line_number, end_index)
            index = end_index

        if not units:
            raise DocumentExtractionError(f"Markdown 没有可建立索引的非空内容: {source.name}")

        content_hash = _content_hash(raw)
        return ParsedDocument(
            source=DocumentSource(
                document_id=content_hash,
                document_name=source.name,
                format="markdown",
                source_path=str(source),
                content_hash=content_hash,
                source_locator_scheme="markdown-heading-line-v1",
            ),
            units=units,
        )
