from __future__ import annotations

import sqlite3
from pathlib import Path

from .errors import DatabaseError


def backup_sqlite(source: str | Path, destination: str | Path, *, overwrite: bool = False) -> dict[str, object]:
    source_path = Path(source)
    destination_path = Path(destination)
    if not source_path.exists():
        raise DatabaseError(f"SQLite 源文件不存在: {source_path}")
    if destination_path.exists() and not overwrite:
        raise DatabaseError(f"SQLite 备份文件已存在，未覆盖: {destination_path}")
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    source_connection: sqlite3.Connection | None = None
    destination_connection: sqlite3.Connection | None = None
    try:
        source_connection = sqlite3.connect(str(source_path), timeout=10)
        destination_connection = sqlite3.connect(str(destination_path), timeout=10)
        with destination_connection:
            source_connection.backup(destination_connection)
        integrity = destination_connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise DatabaseError(f"SQLite 备份完整性检查失败: {integrity}")
        return {
            "status": "ok",
            "source": str(source_path),
            "destination": str(destination_path),
            "integrity_check": integrity,
        }
    except sqlite3.Error as exc:
        raise DatabaseError(f"SQLite 备份失败: {exc}") from exc
    finally:
        if source_connection is not None:
            source_connection.close()
        if destination_connection is not None:
            destination_connection.close()
