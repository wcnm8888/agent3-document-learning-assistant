from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"环境变量 {name} 必须是整数") from exc
    if value <= 0:
        raise ValueError(f"环境变量 {name} 必须大于 0")
    return value


def _float_env(name: str, default: float) -> float:
    raw = os.getenv(name, str(default)).strip()
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"环境变量 {name} 必须是数字") from exc
    if value < 0:
        raise ValueError(f"环境变量 {name} 必须大于等于 0")
    return value


def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"环境变量 {name} 必须是布尔值（true/false）")


def _thinking_mode_env(name: str, default: str) -> str:
    value = os.getenv(name, default).strip().lower()
    if value not in {"enabled", "disabled"}:
        raise ValueError(f"环境变量 {name} 必须是 enabled 或 disabled")
    return value


def _collection_model_name(model_name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", model_name).strip("-")


@dataclass(frozen=True)
class ContextConfig:
    max_input_tokens: int = 18_000
    max_input_chars: int = 20_000
    pinned_reserve_ratio: float = 0.10
    evidence_max_chars: int = 12_000
    history_turn_limit: int = 6
    history_max_chars: int = 4_000
    reference_hint_max_chars: int = 600
    note_limit: int = 3
    notes_max_chars: int = 2_000
    min_relevance: float = 0.10
    relevance_weight: float = 0.70
    recency_weight: float = 0.30
    min_evidence_chars: int = 512
    enable_compression: bool = True
    truncation_marker: str = "[…内容已截断…]"

    def __post_init__(self) -> None:
        positive_ints = {
            "max_input_tokens": self.max_input_tokens,
            "max_input_chars": self.max_input_chars,
            "evidence_max_chars": self.evidence_max_chars,
            "history_turn_limit": self.history_turn_limit,
            "history_max_chars": self.history_max_chars,
            "reference_hint_max_chars": self.reference_hint_max_chars,
            "note_limit": self.note_limit,
            "notes_max_chars": self.notes_max_chars,
            "min_evidence_chars": self.min_evidence_chars,
        }
        for name, value in positive_ints.items():
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"ContextConfig {name} 必须是大于 0 的整数")

        ratios = {
            "pinned_reserve_ratio": self.pinned_reserve_ratio,
            "min_relevance": self.min_relevance,
            "relevance_weight": self.relevance_weight,
            "recency_weight": self.recency_weight,
        }
        for name, value in ratios.items():
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"ContextConfig {name} 必须是数字")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"ContextConfig {name} 必须在 [0, 1] 范围内")
        if abs(self.relevance_weight + self.recency_weight - 1.0) > 1e-9:
            raise ValueError("ContextConfig 相关性权重与新近性权重之和必须等于 1")
        if self.min_evidence_chars > self.evidence_max_chars:
            raise ValueError("ContextConfig min_evidence_chars 不能超过 evidence_max_chars")
        if not isinstance(self.enable_compression, bool):
            raise ValueError("ContextConfig enable_compression 必须是布尔值")
        if not isinstance(self.truncation_marker, str) or not self.truncation_marker.strip():
            raise ValueError("ContextConfig truncation_marker 不能为空")

    @classmethod
    def from_settings(cls, settings: "Settings") -> "ContextConfig":
        return cls(
            evidence_max_chars=settings.retrieval_context_max_chars,
            history_turn_limit=settings.memory_turn_limit,
            history_max_chars=settings.memory_context_max_chars,
        )


@dataclass(frozen=True)
class Settings:
    embedding_model: str = "text-embedding-v4"
    embedding_dimension: int = 1024
    embedding_api_key: str | None = None
    embedding_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    embedding_batch_size: int = 10
    embedding_max_retries: int = 3
    embedding_retry_backoff_seconds: float = 1.0
    qdrant_url: str | None = None
    qdrant_api_key: str | None = None
    qdrant_local_path: Path = Path("data/qdrant")
    qdrant_timeout: int = 10
    collection_prefix: str = "docqa"
    chunk_size: int = 1200
    chunk_overlap: int = 160
    deepseek_api_key: str | None = None
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"
    deepseek_thinking: str = "disabled"
    deepseek_trust_env: bool = False
    deepseek_max_retries: int = 2
    deepseek_retry_backoff_seconds: float = 1.0
    retrieval_top_k: int = 5
    retrieval_score_threshold: float = 0.45
    retrieval_context_max_chars: int = 12000
    sqlite_path: Path = Path("data/docqa.sqlite3")
    memory_turn_limit: int = 6
    memory_context_max_chars: int = 4000

    @classmethod
    def from_env(cls, env_file: str | Path | None = None) -> "Settings":
        if env_file:
            load_dotenv(env_file, override=False)
        else:
            load_dotenv(override=False)

        model = os.getenv("EMBED_MODEL_NAME", cls.embedding_model).strip()
        dimension = _int_env("EMBED_VECTOR_DIMENSION", cls.embedding_dimension)
        chunk_size = _int_env("CHUNK_SIZE", cls.chunk_size)
        chunk_overlap = _int_env("CHUNK_OVERLAP", cls.chunk_overlap)
        if chunk_overlap >= chunk_size:
            raise ValueError("CHUNK_OVERLAP 必须小于 CHUNK_SIZE")

        local_path = Path(os.getenv("QDRANT_LOCAL_PATH", str(cls.qdrant_local_path)))
        prefix = os.getenv("QDRANT_COLLECTION_PREFIX", cls.collection_prefix).strip()
        if not prefix:
            raise ValueError("QDRANT_COLLECTION_PREFIX 不能为空")
        sqlite_path = Path(os.getenv("SQLITE_PATH", str(cls.sqlite_path)))

        settings = cls(
            embedding_model=model,
            embedding_dimension=dimension,
            embedding_api_key=os.getenv("EMBED_API_KEY") or os.getenv("DASHSCOPE_API_KEY"),
            embedding_base_url=os.getenv("EMBED_BASE_URL", cls.embedding_base_url).strip(),
            embedding_batch_size=_int_env("EMBED_BATCH_SIZE", cls.embedding_batch_size),
            embedding_max_retries=_int_env("EMBED_MAX_RETRIES", cls.embedding_max_retries),
            embedding_retry_backoff_seconds=_float_env(
                "EMBED_RETRY_BACKOFF_SECONDS", cls.embedding_retry_backoff_seconds
            ),
            qdrant_url=os.getenv("QDRANT_URL") or None,
            qdrant_api_key=os.getenv("QDRANT_API_KEY") or None,
            qdrant_local_path=local_path,
            qdrant_timeout=_int_env("QDRANT_TIMEOUT", cls.qdrant_timeout),
            collection_prefix=prefix,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            deepseek_api_key=os.getenv("DEEPSEEK_API_KEY") or None,
            deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", cls.deepseek_base_url).strip(),
            deepseek_model=os.getenv("DEEPSEEK_MODEL", cls.deepseek_model).strip(),
            deepseek_thinking=_thinking_mode_env("DEEPSEEK_THINKING", cls.deepseek_thinking),
            deepseek_trust_env=_bool_env("DEEPSEEK_TRUST_ENV", cls.deepseek_trust_env),
            deepseek_max_retries=_int_env("DEEPSEEK_MAX_RETRIES", cls.deepseek_max_retries),
            deepseek_retry_backoff_seconds=_float_env(
                "DEEPSEEK_RETRY_BACKOFF_SECONDS", cls.deepseek_retry_backoff_seconds
            ),
            retrieval_top_k=_int_env("RETRIEVAL_TOP_K", cls.retrieval_top_k),
            retrieval_score_threshold=_float_env(
                "RETRIEVAL_SCORE_THRESHOLD", cls.retrieval_score_threshold
            ),
            retrieval_context_max_chars=_int_env(
                "RETRIEVAL_CONTEXT_MAX_CHARS", cls.retrieval_context_max_chars
            ),
            sqlite_path=sqlite_path,
            memory_turn_limit=_int_env("MEMORY_TURN_LIMIT", cls.memory_turn_limit),
            memory_context_max_chars=_int_env(
                "MEMORY_CONTEXT_MAX_CHARS", cls.memory_context_max_chars
            ),
        )
        settings.context_config
        return settings

    @property
    def collection_name(self) -> str:
        return f"{self.collection_prefix}_{_collection_model_name(self.embedding_model)}_dim{self.embedding_dimension}"

    @property
    def context_config(self) -> ContextConfig:
        return ContextConfig.from_settings(self)
