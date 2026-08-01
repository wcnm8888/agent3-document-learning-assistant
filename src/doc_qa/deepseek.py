from __future__ import annotations

import re
import time
from typing import Protocol

from .errors import DeepSeekApiError


_RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class ChatProvider(Protocol):
    model_name: str

    def generate(self, system_prompt: str, user_prompt: str) -> str: ...


class DeepSeekChatProvider:
    """DeepSeek OpenAI-compatible Chat Completions 适配器。"""

    def __init__(
        self,
        *,
        api_key: str | None,
        base_url: str = "https://api.deepseek.com",
        model_name: str = "deepseek-v4-flash",
        thinking: str = "disabled",
        trust_env: bool = False,
        max_retries: int = 2,
        retry_backoff_seconds: float = 1.0,
        max_tokens: int = 1200,
    ):
        if not api_key:
            raise DeepSeekApiError("缺少 DEEPSEEK_API_KEY，无法调用真实 DeepSeek API")
        if max_retries < 0:
            raise ValueError("max_retries 必须大于等于 0")
        if retry_backoff_seconds < 0:
            raise ValueError("retry_backoff_seconds 必须大于等于 0")
        if max_tokens <= 0:
            raise ValueError("max_tokens 必须大于 0")
        try:
            import httpx
            from openai import OpenAI

            self._http_client = httpx.Client(trust_env=trust_env)
            self._client = OpenAI(
                api_key=api_key,
                base_url=base_url.rstrip("/"),
                http_client=self._http_client,
            )
        except Exception as exc:
            raise DeepSeekApiError(f"DeepSeek 客户端初始化失败: {type(exc).__name__}: {exc}") from exc
        if thinking not in {"enabled", "disabled"}:
            raise ValueError("thinking must be enabled or disabled")
        self.model_name = model_name
        self.thinking = thinking
        self.trust_env = trust_env
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.max_tokens = max_tokens

    @staticmethod
    def _status_code(exc: Exception) -> int | None:
        status = getattr(exc, "status_code", None)
        if isinstance(status, int):
            return status
        response = getattr(exc, "response", None)
        status = getattr(response, "status_code", None)
        return status if isinstance(status, int) else None

    @classmethod
    def _should_retry(cls, exc: Exception) -> bool:
        status = cls._status_code(exc)
        if status is not None:
            return status in _RETRYABLE_STATUS
        name = type(exc).__name__.lower()
        text = str(exc).lower()
        return any(marker in name or marker in text for marker in ("timeout", "connection", "network"))

    @staticmethod
    def _format_error(exc: Exception) -> str:
        status = DeepSeekChatProvider._status_code(exc)
        detail = str(exc).strip() or type(exc).__name__
        detail = re.sub(r"Bearer\s+\S+", "Bearer [REDACTED]", detail, flags=re.IGNORECASE)
        return (
            f"DeepSeek API 调用失败（http_status={status or 'unknown'}, "
            f"retryable={DeepSeekChatProvider._should_retry(exc)}）: {detail}"
        )

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        for attempt in range(self.max_retries + 1):
            try:
                response = self._client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=self.max_tokens,
                    response_format={"type": "json_object"},
                    extra_body={"thinking": {"type": self.thinking}},
                )
                if not response.choices:
                    finish_reason = "no_choices"
                    reasoning_length = 0
                    content = ""
                else:
                    choice = response.choices[0]
                    message = choice.message
                    content = message.content or ""
                    finish_reason = getattr(choice, "finish_reason", None) or "unknown"
                    reasoning_length = len(getattr(message, "reasoning_content", None) or "")
                if not content or not content.strip():
                    if attempt >= self.max_retries:
                        raise DeepSeekApiError(
                            "DeepSeek API returned empty content after retries "
                            f"(finish_reason={finish_reason}, reasoning_length={reasoning_length})"
                        )
                    delay = self.retry_backoff_seconds * (2**attempt)
                    if delay > 0:
                        time.sleep(delay)
                    continue
                return content.strip()
            except DeepSeekApiError:
                raise
            except Exception as exc:
                if not self._should_retry(exc) or attempt >= self.max_retries:
                    raise DeepSeekApiError(self._format_error(exc)) from exc
                delay = self.retry_backoff_seconds * (2**attempt)
                if delay > 0:
                    time.sleep(delay)
        raise AssertionError("unreachable")
