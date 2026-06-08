from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.app.identity.domain.model.entities import FaceSample, PersonAggregate
from src.app.biometrics.domain.model.valueobjects import FaceEmbedding, ConfidenceScore, SimilarityScore
from src.app.biometrics.domain.model.results import IdentificationMatchResult
from src.app.identity.domain.model.valueobjects import PersonId, PersonName, PeruvianDni
from src.app.identity.domain.repositories import PersonRepository


class MongoDbPersonRepository(PersonRepository):
    def __init__(self, database: AsyncIOMotorDatabase, max_embeddings_per_person: int = 10) -> None:
        self._collection = database.persons
        self._max_embeddings_per_person = max(1, int(max_embeddings_per_person))

    @staticmethod
    def _normalize(values: tuple[float, ...]) -> np.ndarray:
        vec = np.asarray(values, dtype=np.float32).reshape(-1)
        vec /= max(1e-6, float(np.linalg.norm(vec)))
        return vec

    def _to_domain(self, doc: dict) -> PersonAggregate:
        samples = tuple(
            FaceSample(
                embedding=FaceEmbedding(tuple(emb))
            )
            for emb in doc.get("embeddings", [])
        )
        return PersonAggregate(
            person_id=PersonId(doc["person_id"]),
            first_name=PersonName(doc["first_name"]),
            last_name=PersonName(doc["last_name"]),
            dni=PeruvianDni(doc["dni"]),
            image_url=doc.get("image_url") or doc.get("photo_base64"),
            samples=samples,
        )

    async def find_by_id(self, person_id: PersonId) -> PersonAggregate | None:
        doc = await self._collection.find_one({"person_id": person_id.value})
        if doc is None:
            return None
        return self._to_domain(doc)

    async def find_by_dni(self, dni: PeruvianDni) -> PersonAggregate | None:
        doc = await self._collection.find_one({"dni": dni.value})
        if doc is None:
            return None
        return self._to_domain(doc)

    async def save(self, person: PersonAggregate) -> PersonAggregate:
        now_epoch = int(datetime.now(UTC).timestamp())
        
        kept_samples = (
            person.samples[-self._max_embeddings_per_person :]
            if len(person.samples) > self._max_embeddings_per_person
            else person.samples
        )
        
        embeddings_data = []
        for sample in kept_samples:
            vec = self._normalize(sample.embedding.values)
            embeddings_data.append(vec.tolist())

        update_data = {
            "first_name": person.first_name.value,
            "last_name": person.last_name.value,
            "dni": person.dni.value,
            "image_url": person.image_url,
            "embeddings": embeddings_data,
            "updated_at": now_epoch,
        }

        await self._collection.update_one(
            {"person_id": person.person_id.value},
            {
                "$set": update_data,
                "$setOnInsert": {"created_at": now_epoch}
            },
            upsert=True
        )

        return PersonAggregate(
            person_id=person.person_id,
            first_name=person.first_name,
            last_name=person.last_name,
            dni=person.dni,
            image_url=person.image_url,
            samples=tuple(kept_samples),
        )

    async def find_best_match(self, embedding: FaceEmbedding) -> IdentificationMatchResult | None:
        query_vec = self._normalize(embedding.values)
        
        cursor = self._collection.find({}, {"person_id": 1, "embeddings": 1})
        rows = await cursor.to_list(length=None)
        
        if not rows:
            return None

        best_person_id: str | None = None
        best_similarity: float | None = None

        for row in rows:
            for emb_list in row.get("embeddings", []):
                vec = np.array(emb_list, dtype=np.float32)
                if vec.size == 0:
                    continue
                vec /= max(1e-6, float(np.linalg.norm(vec)))
                similarity = float(np.dot(query_vec, vec))
                if best_similarity is None or similarity > best_similarity:
                    best_similarity = similarity
                    best_person_id = row["person_id"]

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
        
        query_filter: dict = {}
        if dni:
            query_filter["dni"] = dni
        elif search_term:
            query_filter["$or"] = [
                {"first_name": {"$regex": search_term, "$options": "i"}},
                {"last_name": {"$regex": search_term, "$options": "i"}},
                {"dni": {"$regex": search_term, "$options": "i"}}
            ]
            
        total = await self._collection.count_documents(query_filter)

        cursor = (
            self._collection.find(query_filter)
            .sort([("created_at", -1), ("person_id", 1)])
            .skip(offset)
            .limit(page_size)
        )
        docs = await cursor.to_list(length=page_size)
        
        return (
            tuple(
                PersonAggregate(
                    person_id=PersonId(doc["person_id"]),
                    first_name=PersonName(doc["first_name"]),
                    last_name=PersonName(doc["last_name"]),
                    dni=PeruvianDni(doc["dni"]),
                    image_url=doc.get("image_url") or doc.get("photo_base64"),
                    samples=tuple(),
                )
                for doc in docs
            ),
            total,
        )
