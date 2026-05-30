from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass

import numpy as np

from src.contexts.identification.application.ports import Match, PersonRepository
from src.contexts.identification.domain.model.valueobjects import FaceEmbedding, PersonId


@dataclass(frozen=True, slots=True)
class _RowEmbedding:
    person_id: str
    embedding: bytes  # float32 blob


class SQLitePersonRepository(PersonRepository):
    """SQLite-backed repository for embeddings.

    Stores normalized float32 vectors as BLOB.
    Designed for single-server MVP usage.
    """

    def __init__(self, db_path: str, max_embeddings_per_person: int = 10) -> None:
        self._db_path = str(db_path)
        self._max = int(max_embeddings_per_person)
        if self._max <= 0:
            self._max = 10

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
                CREATE TABLE IF NOT EXISTS embeddings (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  person_id TEXT NOT NULL,
                  embedding BLOB NOT NULL,
                  created_at INTEGER NOT NULL DEFAULT (unixepoch())
                );
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_embeddings_person_id ON embeddings(person_id);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_embeddings_created_at ON embeddings(created_at);"
            )

    @staticmethod
    def _to_vec(embedding: FaceEmbedding) -> np.ndarray:
        v = np.asarray(embedding.values, dtype=np.float32).reshape(-1)
        v /= max(1e-6, float(np.linalg.norm(v)))
        return v

    def upsert_embedding(self, person_id: PersonId, embedding: FaceEmbedding) -> None:
        vec = self._to_vec(embedding)
        blob = vec.tobytes(order="C")

        with self._connect() as conn:
            conn.execute(
                "INSERT INTO embeddings(person_id, embedding) VALUES(?, ?)",
                (person_id.value, sqlite3.Binary(blob)),
            )

            # Keep only the newest N embeddings for this person.
            conn.execute(
                """
                DELETE FROM embeddings
                WHERE person_id = ?
                  AND id NOT IN (
                    SELECT id FROM embeddings
                    WHERE person_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                  );
                """,
                (person_id.value, person_id.value, self._max),
            )

    def best_match(self, embedding: FaceEmbedding) -> Match | None:
        q = self._to_vec(embedding)

        with self._connect() as conn:
            rows = conn.execute(
                "SELECT person_id, embedding FROM embeddings",
            ).fetchall()

        if not rows:
            return None

        best_person: str | None = None
        best_score: float | None = None

        for r in rows:
            # frombuffer returns a read-only view; copy so we can normalize in-place.
            v = np.frombuffer(r["embedding"], dtype=np.float32).copy()
            if v.size == 0:
                continue
            v /= max(1e-6, float(np.linalg.norm(v)))
            score = float(np.dot(q, v))
            if best_score is None or score > best_score:
                best_score = score
                best_person = str(r["person_id"])

        if best_person is None or best_score is None:
            return None
        return Match(person_id=PersonId(best_person), score=best_score)
