from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.db.sqlite_utils import (
    SqliteRunStateLockError,
    acquire_sqlite_runstate_lock,
    release_sqlite_runstate_lock,
    require_sqlite_lifecycle_owner,
    sqlite_runstate_lock_path,
)


def test_serving_owner_guard_preserves_the_primary_lock(tmp_path: Path) -> None:
    database = tmp_path / "store.db"
    sqlite3.connect(database).close()
    owner = acquire_sqlite_runstate_lock(database)
    try:
        require_sqlite_lifecycle_owner(f"sqlite+aiosqlite:///{database}")
        with pytest.raises(SqliteRunStateLockError):
            acquire_sqlite_runstate_lock(database)
    finally:
        release_sqlite_runstate_lock(owner)
    with pytest.raises(RuntimeError, match="live SQLite lifecycle owner"):
        require_sqlite_lifecycle_owner(f"sqlite+aiosqlite:///{database}")


@pytest.mark.parametrize("store_exists", [False, True])
def test_serving_owner_guard_does_not_create_missing_state(tmp_path: Path, store_exists: bool) -> None:
    database = tmp_path / "store.db"
    if store_exists:
        sqlite3.connect(database).close()
    with pytest.raises(RuntimeError):
        require_sqlite_lifecycle_owner(f"sqlite+aiosqlite:///{database}")
    assert database.exists() is store_exists
    assert not sqlite_runstate_lock_path(database).exists()


def test_serving_owner_guard_rejects_non_sqlite_store() -> None:
    with pytest.raises(RuntimeError, match="local SQLite store"):
        require_sqlite_lifecycle_owner("postgresql+asyncpg://localhost/isolated_test")
