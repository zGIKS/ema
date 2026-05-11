from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.contexts.identification.application.ports import Match, PersonRepository
from src.contexts.identification.domain.model.valueobjects import FaceEmbedding, PersonId


@dataclass
class _Row:
    person_id: PersonId
    vec: np.ndarray  # normalized float32


class InMemoryPersonRepository(PersonRepository):
    def __init__(self) -> None:
        self._rows: list[_Row] = []

    def upsert_embedding(self, person_id: PersonId, embedding: FaceEmbedding) -> None:
        vec = np.asarray(embedding.values, dtype=np.float32).reshape(-1)
        vec /= max(1e-6, float(np.linalg.norm(vec)))

        # Replace existing entry for the person if present, else append.
        for r in self._rows:
            if r.person_id.value == person_id.value:
                r.vec = vec
                return
        self._rows.append(_Row(person_id=person_id, vec=vec))

    def best_match(self, embedding: FaceEmbedding) -> Match | None:
        if not self._rows:
            return None

        q = np.asarray(embedding.values, dtype=np.float32).reshape(-1)
        q /= max(1e-6, float(np.linalg.norm(q)))

        best: tuple[PersonId, float] | None = None
        for r in self._rows:
            # cosine similarity since vectors are normalized
            score = float(np.dot(q, r.vec))
            if best is None or score > best[1]:
                best = (r.person_id, score)

        assert best is not None
        return Match(person_id=best[0], score=best[1])

