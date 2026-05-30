from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from src.contexts.identification.application.ports import Match, PersonRepository
from src.contexts.identification.domain.model.valueobjects import FaceEmbedding, PersonId


@dataclass
class _Row:
    person_id: PersonId
    vecs: list[np.ndarray] = field(default_factory=list)  # normalized float32 vectors


class InMemoryPersonRepository(PersonRepository):
    def __init__(self, max_embeddings_per_person: int = 10) -> None:
        self._rows: list[_Row] = []
        self._max = int(max_embeddings_per_person)

    def upsert_embedding(self, person_id: PersonId, embedding: FaceEmbedding) -> None:
        vec = np.asarray(embedding.values, dtype=np.float32).reshape(-1)
        vec /= max(1e-6, float(np.linalg.norm(vec)))

        # Add embedding for the person if present, else create a new row.
        for r in self._rows:
            if r.person_id.value == person_id.value:
                r.vecs.append(vec)
                if len(r.vecs) > self._max:
                    r.vecs = r.vecs[-self._max :]
                return
        self._rows.append(_Row(person_id=person_id, vecs=[vec]))

    def best_match(self, embedding: FaceEmbedding) -> Match | None:
        if not self._rows:
            return None

        q = np.asarray(embedding.values, dtype=np.float32).reshape(-1)
        q /= max(1e-6, float(np.linalg.norm(q)))

        best: tuple[PersonId, float] | None = None
        for r in self._rows:
            for v in r.vecs:
                # cosine similarity since vectors are normalized
                score = float(np.dot(q, v))
                if best is None or score > best[1]:
                    best = (r.person_id, score)

        assert best is not None
        return Match(person_id=best[0], score=best[1])
