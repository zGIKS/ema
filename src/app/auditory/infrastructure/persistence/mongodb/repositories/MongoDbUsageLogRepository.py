from __future__ import annotations

from datetime import UTC, datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.app.auditory.domain.repositories.UsageLogRepository import UsageLogRepository
from src.app.auditory.domain.model.entities.UsageLog import UsageLog


class MongoDbUsageLogRepository(UsageLogRepository):
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self._collection = database.usage_logs

    async def log_identify(
        self,
        *,
        user_id: str,
        person_id: str | None,
        first_name: str | None = None,
        last_name: str | None = None,
        dni: str | None = None,
        confidence: float | None,
        duration_ms: int,
        image_url: str | None = None,
    ) -> None:
        await self._collection.insert_one(
            {
                "user_id": user_id,
                "operation": "identify",
                "person_id": person_id,
                "first_name": first_name,
                "last_name": last_name,
                "dni": dni,
                "confidence": float(confidence) if confidence is not None else None,
                "duration_ms": int(duration_ms),
                "image_url": image_url,
                "used_at": int(datetime.now(UTC).timestamp()),
            }
        )

    async def log_register(
        self,
        *,
        user_id: str,
        person_id: str,
        first_name: str,
        last_name: str,
        dni: str,
        duration_ms: int,
        image_url: str | None = None,
    ) -> None:
        await self._collection.insert_one(
            {
                "user_id": user_id,
                "operation": "register",
                "person_id": person_id,
                "first_name": first_name,
                "last_name": last_name,
                "dni": dni,
                "confidence": None,
                "duration_ms": int(duration_ms),
                "image_url": image_url,
                "used_at": int(datetime.now(UTC).timestamp()),
            }
        )

    async def log_add_person_face_samples(
        self,
        *,
        user_id: str,
        person_id: str,
        first_name: str,
        last_name: str,
        dni: str,
        samples_added: int,
        total_samples: int,
        duration_ms: int,
    ) -> None:
        await self._collection.insert_one(
            {
                "user_id": user_id,
                "operation": "add_face_samples",
                "person_id": person_id,
                "first_name": first_name,
                "last_name": last_name,
                "dni": dni,
                "confidence": None,
                "samples_added": int(samples_added),
                "total_samples": int(total_samples),
                "duration_ms": int(duration_ms),
                "used_at": int(datetime.now(UTC).timestamp()),
            }
        )

    async def find_paginated(
        self,
        *,
        page: int,
        page_size: int,
        user_id: str | None = None,
    ) -> tuple[tuple[UsageLog, ...], int]:
        offset = (page - 1) * page_size
        query_filter = {"user_id": user_id} if user_id is not None else {}
        total = await self._collection.count_documents(query_filter)

        cursor = (
            self._collection.find(query_filter)
            .sort("used_at", -1)
            .skip(offset)
            .limit(page_size)
        )
        docs = await cursor.to_list(length=page_size)
        
        return (
            tuple(
                UsageLog(
                    user_id=doc.get("user_id"),
                    operation=doc["operation"],
                    person_id=doc.get("person_id"),
                    first_name=doc.get("first_name"),
                    last_name=doc.get("last_name"),
                    dni=doc.get("dni"),
                    confidence=doc.get("confidence"),
                    samples_added=doc.get("samples_added"),
                    total_samples=doc.get("total_samples"),
                    duration_ms=doc["duration_ms"],
                    image_url=doc.get("image_url"),
                    used_at=doc["used_at"],
                )
                for doc in docs
            ),
            total,
        )
