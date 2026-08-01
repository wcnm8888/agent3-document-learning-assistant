from __future__ import annotations

import math
import re
import time
from typing import Protocol

from .errors import EmbeddingApiError, EmbeddingDimensionMismatch, EmbeddingServiceError


_MAX_BATCH_SIZE = 10
_RETRYABLE_HTTP_STATUS = {429, 500, 502, 503, 504}


class EmbeddingProvider(Protocol):
    model_name: str
    dimension: int

    def encode(self, texts: list[str]) -> list[list[float]]: ...


class DashScopeEmbeddingProvider:
    """复用 hello-agents 的适配器，但显式固定模型和维度。"""

    def __init__(
        self,
        model_name: str,
        expected_dimension: int,
        api_key: str | None,
        base_url: str,
        batch_size: int = 10,
        max_retries: int = 3,
        retry_backoff_seconds: float = 1.0,
    ):
        if batch_size <= 0:
            raise ValueError("batch_size 必须大于 0")
        if batch_size > _MAX_BATCH_SIZE:
            raise EmbeddingServiceError(
                f"{model_name} 单次最多支持 {_MAX_BATCH_SIZE} 条文本，当前 batch_size={batch_size}"
            )
        if max_retries < 0:
            raise ValueError("max_retries 必须大于等于 0")
        if retry_backoff_seconds < 0:
            raise ValueError("retry_backoff_seconds 必须大于等于 0")
        if not api_key:
            raise EmbeddingServiceError("缺少 EMBED_API_KEY 或 DASHSCOPE_API_KEY，无法调用真实 Embedding API")

        self.model_name = model_name
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self._client = self._create_client(model_name, api_key, base_url)
        self.dimension = int(getattr(self._client, "dimension", 0))
        if self.dimension != expected_dimension:
            raise EmbeddingDimensionMismatch(
                f"Embedding 模型 {model_name} 返回维度 {self.dimension}，期望 {expected_dimension}"
            )

    def _create_client(self, model_name: str, api_key: str, base_url: str):
        try:
            from hello_agents.memory.embedding import DashScopeEmbedding
        except Exception as exc:
            raise EmbeddingApiError(
                f"Embedding 适配器导入失败: {type(exc).__name__}: {exc}"
            ) from exc

        for attempt in range(self.max_retries + 1):
            try:
                return DashScopeEmbedding(
                    model_name=model_name,
                    api_key=api_key,
                    base_url=base_url or None,
                )
            except Exception as exc:
                if not self._should_retry(exc) or attempt >= self.max_retries:
                    raise EmbeddingApiError(
                        self._format_error("初始化/健康检查", exc)
                    ) from exc
                self._sleep_before_retry(attempt)

        raise AssertionError("unreachable")

    @staticmethod
    def _status_code(exc: Exception) -> int | None:
        response = getattr(exc, "response", None)
        status = getattr(response, "status_code", None)
        if isinstance(status, int):
            return status
        match = re.search(r"(?:失败|status)[^0-9]*(\d{3})", str(exc), flags=re.IGNORECASE)
        return int(match.group(1)) if match else None

    @classmethod
    def _should_retry(cls, exc: Exception) -> bool:
        status = cls._status_code(exc)
        if status is not None:
            return status in _RETRYABLE_HTTP_STATUS
        error_name = type(exc).__name__.lower()
        error_text = str(exc).lower()
        return any(
            marker in error_name or marker in error_text
            for marker in ("timeout", "connection", "connecterror", "proxy", "network")
        )

    def _sleep_before_retry(self, attempt: int) -> None:
        delay = self.retry_backoff_seconds * (2**attempt)
        if delay > 0:
            time.sleep(delay)

    @staticmethod
    def _format_error(phase: str, exc: Exception, batch_size: int | None = None) -> str:
        raw = str(exc).strip() or type(exc).__name__
        raw = re.sub(r"Bearer\s+\S+", "Bearer [REDACTED]", raw, flags=re.IGNORECASE)
        status = DashScopeEmbeddingProvider._status_code(exc)
        provider_code_match = re.search(r'"code"\s*:\s*"([^"]+)"', raw)
        provider_code = provider_code_match.group(1) if provider_code_match else "unknown"
        retryable = DashScopeEmbeddingProvider._should_retry(exc)
        batch_detail = f", batch_size={batch_size}" if batch_size is not None else ""
        return (
            f"Embedding API {phase}失败"
            f"（http_status={status or 'unknown'}, provider_code={provider_code}"
            f", retryable={retryable}{batch_detail}）: {raw}"
        )

    def _encode_batch(self, batch: list[str], batch_number: int) -> list[list[float]]:
        for attempt in range(self.max_retries + 1):
            try:
                raw_vectors = self._client.encode(batch)
                return [list(map(float, vector)) for vector in raw_vectors]
            except Exception as exc:
                if not self._should_retry(exc) or attempt >= self.max_retries:
                    message = self._format_error(
                        f"第 {batch_number} 批调用", exc, batch_size=len(batch)
                    )
                    raise EmbeddingApiError(message) from exc
                self._sleep_before_retry(attempt)
        raise AssertionError("unreachable")

    def encode(self, texts: list[str]) -> list[list[float]]:
        if not texts or any(not text.strip() for text in texts):
            raise EmbeddingServiceError("Embedding 输入不能为空")
        vectors: list[list[float]] = []
        for start in range(0, len(texts), self.batch_size):
            batch = texts[start : start + self.batch_size]
            vectors.extend(self._encode_batch(batch, start // self.batch_size + 1))
        if len(vectors) != len(texts):
            raise EmbeddingServiceError("Embedding API 返回数量与输入分块数量不一致")
        for vector in vectors:
            if len(vector) != self.dimension or not all(math.isfinite(v) for v in vector):
                raise EmbeddingDimensionMismatch(
                    f"Embedding 返回向量维度或数值非法：实际 {len(vector)}，期望 {self.dimension}"
                )
        return vectors
