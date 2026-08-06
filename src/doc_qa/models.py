from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Mapping
from urllib.parse import quote


EMBEDDING_PROFILE = "text-embedding-v4:1024"
CONTEXT_PACKET_KINDS = frozenset(
    {"policy", "task", "rag_evidence", "conversation", "note", "output_contract"}
)
PINNED_CONTEXT_PACKET_KINDS = frozenset({"policy", "task", "output_contract"})
RAG_EVIDENCE_METADATA = frozenset(
    {"citation_id", "document_id", "chunk_id", "source_locator"}
)
RESERVED_CONTEXT_METADATA = frozenset({"kind", "evidence_eligible", "pinned"})


def estimate_tokens(text: str) -> int:
    """对中英文混合文本做确定、保守且无外部依赖的 Token 估算。"""
    if not isinstance(text, str):
        raise TypeError("Token 估算输入必须是字符串")
    if not text:
        return 0

    chinese_chars = sum(1 for char in text if "\u4e00" <= char <= "\u9fff")
    ascii_words = re.findall(r"[A-Za-z0-9_]+", text)
    ascii_word_tokens = math.ceil(len(ascii_words) * 1.3)
    ascii_content_chars = sum(len(word) for word in ascii_words)
    ascii_length_tokens = math.ceil(ascii_content_chars / 4)
    other_non_whitespace = sum(
        1
        for char in text
        if not char.isspace()
        and not ("\u4e00" <= char <= "\u9fff")
        and not (char.isascii() and (char.isalnum() or char == "_"))
    )
    punctuation_tokens = math.ceil(other_non_whitespace / 2)
    return max(
        1,
        chinese_chars + max(ascii_word_tokens, ascii_length_tokens) + punctuation_tokens,
    )


@dataclass(frozen=True)
class ContextPacket:
    """GSSC 候选信息包；事实权限只能由 kind 派生。"""

    packet_id: str
    kind: str
    content: str
    timestamp: datetime
    relevance_score: float = 0.5
    stable_order: int = 0
    metadata: Mapping[str, object] = field(default_factory=dict)
    char_count: int = field(init=False)
    estimated_tokens: int = field(init=False)
    evidence_eligible: bool = field(init=False)
    pinned: bool = field(init=False)

    def __post_init__(self) -> None:
        packet_id = self.packet_id.strip() if isinstance(self.packet_id, str) else ""
        if not packet_id:
            raise ValueError("ContextPacket packet_id 不能为空")
        if self.kind not in CONTEXT_PACKET_KINDS:
            raise ValueError(f"ContextPacket kind 非法: {self.kind}")
        if not isinstance(self.content, str) or not self.content.strip():
            raise ValueError("ContextPacket content 不能为空")
        if not isinstance(self.timestamp, datetime):
            raise ValueError("ContextPacket timestamp 必须是 datetime")
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("ContextPacket timestamp 必须包含时区")
        if not isinstance(self.relevance_score, (int, float)) or isinstance(
            self.relevance_score, bool
        ):
            raise ValueError("ContextPacket relevance_score 必须是数字")
        relevance_score = float(self.relevance_score)
        if not 0.0 <= relevance_score <= 1.0:
            raise ValueError("ContextPacket relevance_score 必须在 [0, 1] 范围内")
        if not isinstance(self.stable_order, int) or isinstance(self.stable_order, bool):
            raise ValueError("ContextPacket stable_order 必须是整数")
        if self.stable_order < 0:
            raise ValueError("ContextPacket stable_order 必须大于等于 0")
        if not isinstance(self.metadata, Mapping):
            raise ValueError("ContextPacket metadata 必须是映射")

        metadata = dict(self.metadata)
        reserved = RESERVED_CONTEXT_METADATA & metadata.keys()
        if reserved:
            raise ValueError(f"ContextPacket metadata 包含保留字段: {sorted(reserved)}")
        if self.kind == "rag_evidence":
            missing = RAG_EVIDENCE_METADATA - metadata.keys()
            if missing:
                raise ValueError(f"rag_evidence metadata 缺少字段: {sorted(missing)}")
            for key in RAG_EVIDENCE_METADATA:
                if not str(metadata[key]).strip():
                    raise ValueError(f"rag_evidence metadata 字段不能为空: {key}")

        object.__setattr__(self, "packet_id", packet_id)
        object.__setattr__(self, "relevance_score", relevance_score)
        object.__setattr__(self, "metadata", MappingProxyType(metadata))
        object.__setattr__(self, "char_count", len(self.content))
        object.__setattr__(self, "estimated_tokens", estimate_tokens(self.content))
        object.__setattr__(self, "evidence_eligible", self.kind == "rag_evidence")
        object.__setattr__(self, "pinned", self.kind in PINNED_CONTEXT_PACKET_KINDS)


@dataclass(frozen=True)
class ContextBuildResult:
    """ContextBuilder 的只读输出与诊断，不把完整正文写入默认日志。"""

    system_prompt: str
    user_prompt: str
    selected_packet_ids: tuple[str, ...]
    dropped_packet_ids: tuple[str, ...]
    included_citation_ids: tuple[str, ...]
    section_usage: Mapping[str, Mapping[str, int]]
    total_estimated_tokens: int
    total_chars: int
    compression_events: tuple[str, ...] = ()
    drop_reasons: Mapping[str, str] = field(default_factory=dict)
    over_budget: bool = False
    reference_resolution_used: bool = False
    reference_turn_id: str | None = None
    reference_hint_chars: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.system_prompt, str) or not self.system_prompt.strip():
            raise ValueError("ContextBuildResult system_prompt 不能为空")
        if not isinstance(self.user_prompt, str) or not self.user_prompt.strip():
            raise ValueError("ContextBuildResult user_prompt 不能为空")
        if self.total_estimated_tokens < 0 or self.total_chars < 0:
            raise ValueError("ContextBuildResult 预算计数不能为负数")
        if not isinstance(self.reference_resolution_used, bool):
            raise ValueError("ContextBuildResult reference_resolution_used 必须是布尔值")
        if not isinstance(self.reference_hint_chars, int) or isinstance(
            self.reference_hint_chars, bool
        ):
            raise ValueError("ContextBuildResult reference_hint_chars 必须是整数")
        if self.reference_hint_chars < 0:
            raise ValueError("ContextBuildResult reference_hint_chars 不能为负数")
        if not self.reference_resolution_used and (
            self.reference_turn_id is not None or self.reference_hint_chars != 0
        ):
            raise ValueError("未使用指代解析时不能携带指代诊断")

        frozen_usage: dict[str, Mapping[str, int]] = {}
        for section, usage in self.section_usage.items():
            normalized = dict(usage)
            if any(not isinstance(value, int) or value < 0 for value in normalized.values()):
                raise ValueError(f"ContextBuildResult section_usage 非法: {section}")
            frozen_usage[str(section)] = MappingProxyType(normalized)

        object.__setattr__(self, "selected_packet_ids", tuple(self.selected_packet_ids))
        object.__setattr__(self, "dropped_packet_ids", tuple(self.dropped_packet_ids))
        object.__setattr__(self, "included_citation_ids", tuple(self.included_citation_ids))
        object.__setattr__(self, "section_usage", MappingProxyType(frozen_usage))
        object.__setattr__(self, "compression_events", tuple(self.compression_events))
        object.__setattr__(self, "drop_reasons", MappingProxyType(dict(self.drop_reasons)))


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
