from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.contexts.identification.domain.model.valueobjects import FaceEmbedding, PersonId


@dataclass(frozen=True, slots=True)
class Match:
    person_id: PersonId
    score: float  # cosine similarity in [ -1, 1 ]


class PersonRepository(Protocol):
    def upsert_embedding(self, person_id: PersonId, embedding: FaceEmbedding) -> None: ...

    def best_match(self, embedding: FaceEmbedding) -> Match | None: ...

