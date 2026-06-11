from __future__ import annotations

from math import sqrt

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.biometrics.domain.model.results import IdentificationMatchResult
from src.app.biometrics.domain.model.valueobjects import ConfidenceScore, FaceEmbedding, SimilarityScore
from src.app.identity.domain.model.entities import FaceSample, PersonAggregate
from src.app.identity.domain.model.valueobjects import PersonId, PersonName, PeruvianDni
from src.app.identity.domain.repositories import PersonRepository
from src.app.identity.infrastructure.persistence.sqlalchemy.models import PersonModel


class SqlAlchemyPersonRepository(PersonRepository):
    def __init__(self, session: AsyncSession, max_embeddings_per_person: int = 10) -> None:
        self._session = session
        self._max_embeddings_per_person = max(1, int(max_embeddings_per_person))

    @staticmethod
    def _normalize(values: tuple[float, ...]) -> tuple[float, ...]:
        vec = tuple(float(v) for v in values)
        norm = sqrt(sum(v * v for v in vec))
        if norm <= 1e-6:
            return vec
        return tuple(v / norm for v in vec)

    @staticmethod
    def _to_samples_payload(person: PersonAggregate) -> list[dict[str, object]]:
        return [
            {
                "embedding": list(sample.embedding.values),
                "image_url": sample.image_url,
            }
            for sample in person.samples
        ]

    @staticmethod
    def _to_domain(model: PersonModel) -> PersonAggregate:
        samples = tuple(
            FaceSample(
                embedding=FaceEmbedding(tuple(sample.get("embedding", []))),
                image_url=sample.get("image_url"),
            )
            for sample in model.samples or []
        )
        return PersonAggregate(
            person_id=PersonId(model.person_id),
            first_name=PersonName(model.first_name),
            last_name=PersonName(model.last_name),
            dni=PeruvianDni(model.dni),
            image_url=model.image_url,
            samples=samples,
        )

    async def find_by_id(self, person_id: PersonId) -> PersonAggregate | None:
        result = await self._session.execute(select(PersonModel).where(PersonModel.person_id == person_id.value))
        model = result.scalar_one_or_none()
        return None if model is None else self._to_domain(model)

    async def find_by_dni(self, dni: PeruvianDni) -> PersonAggregate | None:
        result = await self._session.execute(select(PersonModel).where(PersonModel.dni == dni.value))
        model = result.scalar_one_or_none()
        return None if model is None else self._to_domain(model)

    async def save(self, person: PersonAggregate) -> PersonAggregate:
        kept_samples = (
            person.samples[-self._max_embeddings_per_person :]
            if len(person.samples) > self._max_embeddings_per_person
            else person.samples
        )
        samples_payload = self._to_samples_payload(PersonAggregate(
            person_id=person.person_id,
            first_name=person.first_name,
            last_name=person.last_name,
            dni=person.dni,
            image_url=person.image_url,
            samples=kept_samples,
        ))

        result = await self._session.execute(select(PersonModel).where(PersonModel.person_id == person.person_id.value))
        model = result.scalar_one_or_none()
        if model is None:
            model = PersonModel(
                person_id=person.person_id.value,
                first_name=person.first_name.value,
                last_name=person.last_name.value,
                dni=person.dni.value,
                image_url=person.image_url,
                samples=samples_payload,
            )
            self._session.add(model)
        else:
            model.first_name = person.first_name.value
            model.last_name = person.last_name.value
            model.dni = person.dni.value
            model.image_url = person.image_url
            model.samples = samples_payload

        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def find_best_match(self, embedding: FaceEmbedding) -> IdentificationMatchResult | None:
        query_vec = self._normalize(embedding.values)
        result = await self._session.execute(select(PersonModel.person_id, PersonModel.samples))
        rows = result.all()

        if not rows:
            return None

        best_person_id: str | None = None
        best_similarity: float | None = None

        for person_id, samples in rows:
            for sample in samples or []:
                vec = self._normalize(tuple(sample.get("embedding", [])))
                if not vec:
                    continue
                similarity = sum(a * b for a, b in zip(query_vec, vec, strict=False))
                if best_similarity is None or similarity > best_similarity:
                    best_similarity = similarity
                    best_person_id = person_id

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
        search_term: str | None = None,
        dni: str | None = None,
    ) -> tuple[tuple[PersonAggregate, ...], int]:
        offset = (page - 1) * page_size
        conditions = []
        if dni:
            conditions.append(PersonModel.dni == dni)
        elif search_term:
            pattern = f"%{search_term}%"
            conditions.append(
                or_(
                    PersonModel.first_name.ilike(pattern),
                    PersonModel.last_name.ilike(pattern),
                    PersonModel.dni.ilike(pattern),
                )
            )

        count_stmt = select(func.count()).select_from(PersonModel)
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        total = int((await self._session.execute(count_stmt)).scalar_one())

        stmt = select(PersonModel).order_by(PersonModel.created_at.desc(), PersonModel.person_id.asc()).offset(offset).limit(page_size)
        if conditions:
            stmt = stmt.where(*conditions)
        result = await self._session.execute(stmt)
        docs = result.scalars().all()

        return (
            tuple(self._to_domain(doc) for doc in docs),
            total,
        )
