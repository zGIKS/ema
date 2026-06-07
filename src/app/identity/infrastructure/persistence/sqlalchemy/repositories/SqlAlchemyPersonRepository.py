from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.identity.domain.model.entities import FaceSample, PersonAggregate
from src.app.biometrics.domain.model.valueobjects import FaceEmbedding
from src.app.biometrics.domain.model.valueobjects import ConfidenceScore, SimilarityScore
from src.app.biometrics.domain.model.results import IdentificationMatchResult
from src.app.identity.domain.model.valueobjects import (
    PersonId,
    PersonName,
    PeruvianDni,
)
from src.app.identity.domain.repositories import PersonRepository
from src.app.identity.infrastructure.persistence.sqlalchemy.models.PersonEmbeddingModel import (
    PersonEmbeddingModel,
)
from src.app.identity.infrastructure.persistence.sqlalchemy.models.PersonModel import (
    PersonModel,
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
        person_model = await self._session.get(PersonModel, person_id.value)
        if person_model is None:
            return None

        result = await self._session.execute(
            select(PersonEmbeddingModel)
            .where(PersonEmbeddingModel.person_id == person_id.value)
            .order_by(PersonEmbeddingModel.id.asc())
        )
        rows = result.scalars().all()

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
        return PersonAggregate(
            person_id=person_id,
            first_name=PersonName(person_model.first_name),
            last_name=PersonName(person_model.last_name),
            dni=PeruvianDni(person_model.dni),
            photo=person_model.photo_base64,
            samples=samples,
        )

    async def find_by_dni(self, dni: PeruvianDni) -> PersonAggregate | None:
        result = await self._session.execute(
            select(PersonModel).where(PersonModel.dni == dni.value)
        )
        person_model = result.scalar_one_or_none()
        if person_model is None:
            return None
        return await self.find_by_id(PersonId(person_model.person_id))

    async def save(self, person: PersonAggregate) -> PersonAggregate:
        now_epoch = int(datetime.now(UTC).timestamp())
        existing_person = await self._session.get(PersonModel, person.person_id.value)
        if existing_person is None:
            self._session.add(
                PersonModel(
                    person_id=person.person_id.value,
                    first_name=person.first_name.value,
                    last_name=person.last_name.value,
                    dni=person.dni.value,
                    photo_base64=person.photo,
                    created_at=now_epoch,
                    updated_at=now_epoch,
                )
            )
        else:
            existing_person.first_name = person.first_name.value
            existing_person.last_name = person.last_name.value
            existing_person.dni = person.dni.value
            existing_person.photo_base64 = person.photo
            existing_person.updated_at = now_epoch

        await self._session.execute(
            delete(PersonEmbeddingModel).where(
                PersonEmbeddingModel.person_id == person.person_id.value
            )
        )

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
        return PersonAggregate(
            person_id=person.person_id,
            first_name=person.first_name,
            last_name=person.last_name,
            dni=person.dni,
            photo=person.photo,
            samples=tuple(kept_samples),
        )

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

    async def find_paginated(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[tuple[PersonAggregate, ...], int]:
        offset = (page - 1) * page_size
        total_result = await self._session.execute(select(func.count()).select_from(PersonModel))
        total = int(total_result.scalar_one())

        result = await self._session.execute(
            select(PersonModel)
            .order_by(PersonModel.created_at.desc(), PersonModel.person_id.asc())
            .offset(offset)
            .limit(page_size)
        )
        person_models = result.scalars().all()
        return (
            tuple(
                PersonAggregate(
                    person_id=PersonId(person_model.person_id),
                    first_name=PersonName(person_model.first_name),
                    last_name=PersonName(person_model.last_name),
                    dni=PeruvianDni(person_model.dni),
                    photo=person_model.photo_base64,
                    samples=tuple(),
                )
                for person_model in person_models
            ),
            total,
        )
