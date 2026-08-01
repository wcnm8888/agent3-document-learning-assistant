from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

import pytest

from doc_qa.chunker import PageAwareChunker
from doc_qa.document_catalog import DocumentCatalogService
from doc_qa.document_parser import DocumentParser
from doc_qa.errors import DocumentExtractionError, DocumentNotFoundError
from doc_qa.markdown_parser import MarkdownParser
from doc_qa.memory_store import SQLiteMemoryStore


def test_markdown_parser_preserves_structure_lines_and_untrusted_content(tmp_path: Path) -> None:
    path = tmp_path / "学习笔记.md"
    path.write_text(
        """# 总览

介绍中文内容。

## 第二章

```python
print('<script>不执行</script>')
```

- 列表项一
- 列表项二

| 名称 | 值 |
| --- | --- |
| A | 1 |

### 细节

<script>alert('不执行')</script>
""",
        encoding="utf-8",
    )

    document = MarkdownParser().parse(path)

    assert document.source.format == "markdown"
    assert document.source.document_id == hashlib.sha256(path.read_bytes()).hexdigest()
    assert [unit.section_path for unit in document.units] == [
        "总览",
        "总览 / 第二章",
        "总览 / 第二章",
        "总览 / 第二章",
        "总览 / 第二章 / 细节",
    ]
    assert document.units[1].line_start == 7
    assert document.units[1].line_end == 9
    assert "<script>不执行</script>" in document.units[1].content
    assert "alert('不执行')" in document.units[-1].content
    assert all(unit.page_start is None and unit.page_end is None for unit in document.units)


def test_markdown_setext_and_root_content_are_supported(tmp_path: Path) -> None:
    path = tmp_path / "setext.markdown"
    path.write_text("根段落\n\n章节标题\n---\n\n章节内容", encoding="utf-8")

    units = MarkdownParser().parse(path).units

    assert units[0].section_path == "根文档"
    assert units[1].section_path == "章节标题"
    assert units[1].line_start == 6


@pytest.mark.parametrize(
    "filename, content, error_type",
    [
        ("empty.md", "", DocumentExtractionError),
        ("blank.md", " \n\n\t", DocumentExtractionError),
    ],
)
def test_markdown_empty_content_fails(tmp_path: Path, filename: str, content: str, error_type: type[Exception]) -> None:
    path = tmp_path / filename
    path.write_text(content, encoding="utf-8")
    with pytest.raises(error_type):
        MarkdownParser().parse(path)


def test_markdown_invalid_utf8_extension_and_missing_file_are_locatable(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.md"
    invalid.write_bytes(b"\xff\xfe")
    with pytest.raises(DocumentExtractionError, match="UTF-8"):
        MarkdownParser().parse(invalid)

    invalid_extension = tmp_path / "note.txt"
    invalid_extension.write_text("内容", encoding="utf-8")
    with pytest.raises(DocumentExtractionError):
        MarkdownParser().parse(invalid_extension)
    with pytest.raises(DocumentNotFoundError):
        MarkdownParser().parse(tmp_path / "missing.md")


def test_markdown_chunk_identity_and_locator_are_stable(tmp_path: Path) -> None:
    first = tmp_path / "a.md"
    second = tmp_path / "renamed.md"
    first.write_text("# 标题\n\n一段内容。", encoding="utf-8")
    second.write_bytes(first.read_bytes())
    parser = MarkdownParser()
    parsed_first = parser.parse(first)
    parsed_second = parser.parse(second)
    chunker = PageAwareChunker(chunk_size=100, overlap=0)

    chunks_first = chunker.chunk_document(parsed_first)
    chunks_second = chunker.chunk_document(parsed_second)
    assert parsed_first.source.document_id == parsed_second.source.document_id
    assert chunks_first[0].chunk_id == chunks_second[0].chunk_id
    assert "section=%E6%A0%87%E9%A2%98" in chunks_first[0].source_locator()
    assert "lines=3-3" in chunks_first[0].source_locator()
    assert chunks_first[0].page_start is None

    second.write_text("# 标题\n\n另一段内容。", encoding="utf-8")
    assert parser.parse(second).source.document_id != parsed_first.source.document_id


def test_unified_parser_keeps_pdf_baseline_chunk_ids(tmp_path: Path) -> None:
    baseline = Path("data/reference/Happy-LLM-0727.pdf")
    parser = DocumentParser()
    document = parser.parse(baseline)
    chunks = PageAwareChunker().chunk_document(document)

    assert document.source.format == "pdf"
    assert len(document.units) == 171
    assert len(chunks) == 262
    assert chunks[0].source_locator() == (
        f"Happy-LLM-0727.pdf#page={chunks[0].page_start}&chunk={chunks[0].chunk_id}"
    )


def test_sqlite_legacy_documents_table_is_migrated_in_temp_db(tmp_path: Path) -> None:
    db_path = tmp_path / "legacy.sqlite3"
    connection = sqlite3.connect(db_path)
    connection.execute(
        """CREATE TABLE documents (
            document_id TEXT PRIMARY KEY, document_name TEXT NOT NULL,
            source_path TEXT NOT NULL, pages_with_text INTEGER NOT NULL DEFAULT 0,
            chunk_count INTEGER NOT NULL DEFAULT 0, indexed_point_count INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL, error_message TEXT, updated_at TEXT NOT NULL
        )"""
    )
    connection.execute(
        "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("legacy-id", "old.pdf", "old.pdf", 3, 4, 4, "indexed", None, "2026-01-01T00:00:00+00:00"),
    )
    connection.commit()
    connection.close()

    store = SQLiteMemoryStore(db_path)
    document = store.get_document("legacy-id")
    assert document is not None
    assert document.format == "pdf"
    assert document.content_hash == "legacy-id"
    assert document.source_unit_count == 3
    assert document.created_at == document.updated_at
    assert store._connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    store.close()

    # 迁移必须可重复执行。
    reopened = SQLiteMemoryStore(db_path)
    assert reopened.get_document("legacy-id") == document
    reopened.close()


def test_document_catalog_tracks_metadata_status_and_duplicate(tmp_path: Path) -> None:
    path = tmp_path / "doc.md"
    path.write_text("# 标题\n\n内容", encoding="utf-8")
    source = MarkdownParser().parse(path).source
    store = SQLiteMemoryStore(tmp_path / "catalog.sqlite3")
    catalog = DocumentCatalogService(store)

    created = catalog.register(source, source_unit_count=1, chunk_count=1)
    duplicate = catalog.register(source, source_unit_count=1, chunk_count=1)
    failed = catalog.update_status(source.document_id, "failed", error_message="解析失败")

    assert created.outcome == "created"
    assert duplicate.outcome == "duplicate"
    assert duplicate.document.document_id == source.document_id
    assert failed.status == "failed"
    assert failed.format == "markdown"
    assert failed.source_locator_scheme == "markdown-heading-line-v1"
    store.close()
