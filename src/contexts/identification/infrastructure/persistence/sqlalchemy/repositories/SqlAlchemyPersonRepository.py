from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.contexts.identification.domain.model.entities import FaceSample, PersonAggregate
from src.contexts.identification.domain.model.results import IdentificationMatchResult
from src.contexts.identification.domain.model.valueobjects import (
    ConfidenceScore,
    FaceEmbedding,
    PersonId,
    SimilarityScore,
)
from src.contexts.identification.domain.repositories import PersonRepository
from src.contexts.identification.infrastructure.persistence.sqlalchemy.models.PersonEmbeddingModel import (
    PersonEmbeddingModel,
)


class SqlAlchemyPersonRepository(PersonRepository):
    def __init__(self, session: AsyncSession, max_embeddings_per_person: int = 10) -> None:
        self._session = session
        self._max_embeddings_per_person = max(1, int(max_embeddings_per_person))

    @staticmethod
    def _normalize(values: tuple[float, ...]) -> np.ndarray:
        vec = np.asarray(values, dtype=np.float32).reshape(-1)
        vec /= max(1e-6, float(np.linalg.norm(vec)))
        return vec

    async def find_by_id(self, person_id: PersonId) -> PersonAggregate | None:
        result = await self._session.execute(
            select(PersonEmbeddingModel)
            .where(PersonEmbeddingModel.person_id == person_id.value)
            .order_by(PersonEmbeddingModel.id.asc())
        )
        rows = result.scalars().all()
        if not rows:
            return None

        samples = tuple(
            FaceSample(
                embedding=FaceEmbedding(
                    tuple(
                        float(x)
                        for x in np.frombuffer(row.embedding, dtype=np.float32).tolist()
                    )
                )
            )
            for row in rows
        )
        return PersonAggregate(person_id=person_id, samples=samples)

    async def save(self, person: PersonAggregate) -> PersonAggregate:
        await self._session.execute(
            delete(PersonEmbeddingModel).where(
                PersonEmbeddingModel.person_id == person.person_id.value
            )
        )

        now_epoch = int(datetime.now(UTC).timestamp())
        kept_samples = (
            person.samples[-self._max_embeddings_per_person :]
            if len(person.samples) > self._max_embeddings_per_person
            else person.samples
        )
        for sample in kept_samples:
            vec = self._normalize(sample.embedding.values)
            self._session.add(
                PersonEmbeddingModel(
                    person_id=person.person_id.value,
                    embedding=vec.tobytes(order="C"),
                    created_at=now_epoch,
                )
            )

        await self._session.flush()
        return PersonAggregate(person_id=person.person_id, samples=tuple(kept_samples))

    async def find_best_match(self, embedding: FaceEmbedding) -> IdentificationMatchResult | None:
        query_vec = self._normalize(embedding.values)
        result = await self._session.execute(select(PersonEmbeddingModel))
        rows = result.scalars().all()
        if not rows:
            return None

        best_person_id: str | None = None
        best_similarity: float | None = None

        for row in rows:
            vec = np.frombuffer(row.embedding, dtype=np.float32).copy()
            if vec.size == 0:
                continue
            vec /= max(1e-6, float(np.linalg.norm(vec)))
            similarity = float(np.dot(query_vec, vec))
            if best_similarity is None or similarity > best_similarity:
                best_similarity = similarity
                best_person_id = row.person_id

        if best_person_id is None or best_similarity is None:
            return None

        confidence = max(0.0, min(1.0, (best_similarity + 1.0) / 2.0))
        return IdentificationMatchResult(
            person_id=PersonId(best_person_id),
            similarity=SimilarityScore(best_similarity),
            confidence=ConfidenceScore(confidence),
        )
