from __future__ import annotations

import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import Settings
from .errors import DatabaseError, QdrantUnavailableError
from .qdrant_index import QdrantIndexer


@dataclass(frozen=True)
class CheckResult:
    status: str
    component: str
    details: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _safe_url(value: str) -> str:
    parsed = urlsplit(value)
    hostname = parsed.hostname or ""
    host = hostname
    if parsed.port:
        host = f"{hostname}:{parsed.port}"
    return urlunsplit((parsed.scheme, host, parsed.path, "", ""))


def _configuration_check(settings: Settings) -> CheckResult:
    missing: list[str] = []
    if not settings.embedding_api_key:
        missing.append("EMBED_API_KEY")
    if not settings.deepseek_api_key:
        missing.append("DEEPSEEK_API_KEY")
    if not settings.qdrant_url and not settings.qdrant_local_path:
        missing.append("QDRANT_URL or QDRANT_LOCAL_PATH")
    details: dict[str, object] = {
        "embedding_model": settings.embedding_model,
        "embedding_dimension": settings.embedding_dimension,
        "collection": settings.collection_name,
        "qdrant_url": _safe_url(settings.qdrant_url) if settings.qdrant_url else "local-persistence",
        "sqlite_path": str(settings.sqlite_path),
        "missing_fields": missing,
    }
    return CheckResult("failed" if missing else "ok", "configuration", details)


def _qdrant_healthz(settings: Settings) -> dict[str, object]:
    if not settings.qdrant_url:
        return {"status": "skipped", "mode": "local-persistence"}
    url = settings.qdrant_url.rstrip("/") + "/healthz"
    safe_url = _safe_url(url)
    try:
        request = Request(url, method="GET")
        with urlopen(request, timeout=settings.qdrant_timeout) as response:
            if response.status != 200:
                return {"status": "failed", "url": safe_url, "http_status": response.status}
        return {"status": "ok", "url": safe_url, "http_status": 200}
    except HTTPError as exc:
        return {"status": "failed", "url": safe_url, "http_status": exc.code}
    except (URLError, TimeoutError, OSError) as exc:
        return {"status": "failed", "url": safe_url, "error_type": type(exc).__name__}


def _collection_check(
    collection: str,
    dimension: int,
    settings: Settings,
) -> CheckResult:
    try:
        indexer = QdrantIndexer(
            collection,
            dimension,
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            local_path=settings.qdrant_local_path,
            timeout=settings.qdrant_timeout,
        )
    except QdrantUnavailableError as exc:
        return CheckResult(
            "failed",
            "qdrant_collection",
            {"collection": collection, "error_type": "unavailable", "error": str(exc)},
        )
    try:
        info = indexer.collection_info()
        if info["vector_dimension"] != dimension:
            return CheckResult(
                "failed",
                "qdrant_collection",
                {**info, "error_type": "dimension_mismatch", "expected_dimension": dimension},
            )
        return CheckResult("ok", "qdrant_collection", info)
    except QdrantUnavailableError as exc:
        message = str(exc)
        error_type = "collection_missing" if "不存在" in message else "unavailable"
        return CheckResult(
            "failed",
            "qdrant_collection",
            {"collection": collection, "error_type": error_type, "error": message},
        )
    finally:
        indexer.close()


def _qdrant_check(settings: Settings) -> CheckResult:
    healthz = _qdrant_healthz(settings)
    checks = [
        _collection_check(settings.collection_name, settings.embedding_dimension, settings),
    ]
    if settings.embedding_model == "text-embedding-v4" and settings.embedding_dimension == 1024:
        checks.append(
            _collection_check(
                f"{settings.collection_prefix}_text-embedding-v3_dim1024_eval",
                1024,
                settings,
            )
        )
    failed = healthz["status"] == "failed" or any(item.status == "failed" for item in checks)
    return CheckResult(
        "failed" if failed else "ok",
        "qdrant",
        {"healthz": healthz, "collections": [item.as_dict() for item in checks]},
    )


def _sqlite_check(settings: Settings) -> CheckResult:
    path = Path(settings.sqlite_path)
    if str(path) == ":memory:":
        return CheckResult("failed", "sqlite", {"error_type": "unsupported_memory_database"})
    if not path.exists():
        return CheckResult(
            "failed", "sqlite", {"path": str(path), "error_type": "database_missing"}
        )
    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(
            f"file:{quote(path.resolve().as_posix())}?mode=ro", uri=True
        )
        result = connection.execute("PRAGMA integrity_check").fetchone()[0]
        status = "ok" if result == "ok" else "failed"
        return CheckResult(
            status,
            "sqlite",
            {"path": str(path), "integrity_check": result},
        )
    except sqlite3.Error as exc:
        return CheckResult(
            "failed",
            "sqlite",
            {"path": str(path), "error_type": "database_error", "error": str(exc)},
        )
    finally:
        if connection is not None:
            connection.close()


def run_health_check(settings: Settings) -> dict[str, object]:
    """返回无密钥的机器可读健康报告；该检查不会创建 collection 或写入向量。"""
    checks: list[CheckResult] = [_configuration_check(settings)]
    checks.append(_qdrant_check(settings))
    checks.append(_sqlite_check(settings))
    failed = any(item.status == "failed" for item in checks)
    return {
        "status": "failed" if failed else "ok",
        "checks": [item.as_dict() for item in checks],
    }
