from __future__ import annotations

import os
import sqlite3


class SQLiteUsageLogRepository:
    """SQLite-backed usage log (metrics/audit).

    Stores one row per API call (identify/register), with timestamp and metrics.
    """

    def __init__(self, db_path: str) -> None:
        self._db_path = str(db_path)
        parent = os.path.dirname(os.path.abspath(self._db_path))
        if parent:
            os.makedirs(parent, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS usage_logs (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  operation TEXT NOT NULL,
                  person_id TEXT NULL,
                  confidence REAL NULL,
                  duration_ms INTEGER NOT NULL,
                  used_at INTEGER NOT NULL DEFAULT (unixepoch())
                );
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_usage_logs_used_at ON usage_logs(used_at);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_usage_logs_operation ON usage_logs(operation);"
            )

    def log_identify(
        self,
        *,
        person_id: str | None,
        confidence: float,
        duration_ms: int,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO usage_logs(operation, person_id, confidence, duration_ms)
                VALUES('identify', ?, ?, ?)
                """,
                (person_id, float(confidence), int(duration_ms)),
            )

    def log_register(self, *, person_id: str, duration_ms: int) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO usage_logs(operation, person_id, confidence, duration_ms)
                VALUES('register', ?, NULL, ?)
                """,
                (person_id, int(duration_ms)),
            )

