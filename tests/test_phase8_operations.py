from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from doc_qa.backup import backup_sqlite
from doc_qa.config import Settings
from doc_qa.errors import QdrantUnavailableError
from doc_qa.health import run_health_check
from doc_qa.memory_store import SQLiteMemoryStore


def _settings(tmp_path: Path, *, embedding_key: str | None = "embed-test", deepseek_key: str | None = "deep-test") -> Settings:
    return Settings(
        embedding_api_key=embedding_key,
        deepseek_api_key=deepseek_key,
        qdrant_local_path=tmp_path / "qdrant",
        sqlite_path=tmp_path / "docqa.sqlite3",
    )


def _create_collections(settings: Settings) -> None:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams

    client = QdrantClient(path=str(settings.qdrant_local_path))
    for name in (settings.collection_name, "docqa_text-embedding-v3_dim1024_eval"):
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )
    client.close()


def test_health_check_reports_local_collections_and_sqlite(tmp_path: Path):
    settings = _settings(tmp_path)
    _create_collections(settings)
    with SQLiteMemoryStore(settings.sqlite_path):
        pass

    result = run_health_check(settings)

    assert result["status"] == "ok"
    checks = {item["component"]: item for item in result["checks"]}
    assert checks["configuration"]["details"]["missing_fields"] == []
    assert checks["sqlite"]["details"]["integrity_check"] == "ok"
    assert checks["qdrant"]["details"]["healthz"]["status"] == "skipped"
    collections = checks["qdrant"]["details"]["collections"]
    assert {item["details"]["collection"] for item in collections} == {
        settings.collection_name,
        "docqa_text-embedding-v3_dim1024_eval",
    }


def test_health_check_distinguishes_missing_configuration(tmp_path: Path):
    settings = _settings(tmp_path, embedding_key=None, deepseek_key=None)
    result = run_health_check(settings)
    configuration = next(item for item in result["checks"] if item["component"] == "configuration")
    serialized = json.dumps(result, ensure_ascii=False)

    assert result["status"] == "failed"
    assert configuration["details"]["missing_fields"] == ["EMBED_API_KEY", "DEEPSEEK_API_KEY"]
    assert "embed-test" not in serialized
    assert "deep-test" not in serialized


def test_health_check_distinguishes_missing_collection(tmp_path: Path):
    settings = _settings(tmp_path)
    _create_collections(settings)
    client = sqlite3.connect(settings.sqlite_path)
    client.execute("CREATE TABLE marker (value TEXT)")
    client.commit()
    client.close()

    # 删除 v4 collection 只在隔离的临时 Qdrant 中进行，不能影响真实 collection。
    from qdrant_client import QdrantClient

    qdrant = QdrantClient(path=str(settings.qdrant_local_path))
    qdrant.delete_collection(settings.collection_name)
    qdrant.close()

    result = run_health_check(settings)
    qdrant_result = next(item for item in result["checks"] if item["component"] == "qdrant")
    v4 = next(
        item
        for item in qdrant_result["details"]["collections"]
        if item["details"]["collection"] == settings.collection_name
    )

    assert result["status"] == "failed"
    assert v4["details"]["error_type"] == "collection_missing"


def test_health_check_distinguishes_corrupt_sqlite(tmp_path: Path):
    settings = _settings(tmp_path)
    _create_collections(settings)
    settings.sqlite_path.write_bytes(b"not a sqlite database")

    result = run_health_check(settings)
    sqlite_result = next(item for item in result["checks"] if item["component"] == "sqlite")

    assert result["status"] == "failed"
    assert sqlite_result["details"]["error_type"] == "database_error"


def test_health_check_distinguishes_qdrant_unavailable(tmp_path: Path, monkeypatch):
    settings = _settings(tmp_path)
    with SQLiteMemoryStore(settings.sqlite_path):
        pass

    def fail(*args, **kwargs):
        raise QdrantUnavailableError("Qdrant 客户端初始化失败")

    monkeypatch.setattr("doc_qa.health.QdrantIndexer", fail)
    result = run_health_check(settings)
    qdrant_result = next(item for item in result["checks"] if item["component"] == "qdrant")

    assert result["status"] == "failed"
    assert qdrant_result["details"]["collections"][0]["details"]["error_type"] == "unavailable"


def test_sqlite_backup_is_reopenable_and_integrity_checked(tmp_path: Path):
    settings = _settings(tmp_path)
    with SQLiteMemoryStore(settings.sqlite_path) as store:
        session = store.create_session("session-backup")
        assert session.session_id == "session-backup"

    destination = tmp_path / "backups" / "docqa.sqlite3"
    result = backup_sqlite(settings.sqlite_path, destination)

    assert result["status"] == "ok"
    assert result["integrity_check"] == "ok"
    with SQLiteMemoryStore(destination) as restored:
        assert restored.get_session("session-backup").session_id == "session-backup"


def test_sqlite_backup_does_not_overwrite_without_explicit_flag(tmp_path: Path):
    settings = _settings(tmp_path)
    with SQLiteMemoryStore(settings.sqlite_path):
        pass
    destination = tmp_path / "backup.sqlite3"
    backup_sqlite(settings.sqlite_path, destination)

    try:
        backup_sqlite(settings.sqlite_path, destination)
    except Exception as exc:
        assert "未覆盖" in str(exc)
    else:
        raise AssertionError("expected existing backup to be protected")
