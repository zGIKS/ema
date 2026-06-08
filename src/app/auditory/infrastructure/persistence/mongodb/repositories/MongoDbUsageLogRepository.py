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
        person_id: str,
        first_name: str,
        last_name: str,
        dni: str,
        duration_ms: int,
    ) -> None:
        await self._collection.insert_one(
            {
                "operation": "register",
                "person_id": person_id,
                "first_name": first_name,
                "last_name": last_name,
                "dni": dni,
                "confidence": None,
                "duration_ms": int(duration_ms),
                "used_at": int(datetime.now(UTC).timestamp()),
            }
        )

    async def find_paginated(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[tuple[UsageLog, ...], int]:
        offset = (page - 1) * page_size
        total = await self._collection.count_documents({})

        cursor = (
            self._collection.find({})
            .sort("used_at", -1)
            .skip(offset)
            .limit(page_size)
        )
        docs = await cursor.to_list(length=page_size)
        
        return (
            tuple(
                UsageLog(
                    operation=doc["operation"],
                    person_id=doc.get("person_id"),
                    first_name=doc.get("first_name"),
                    last_name=doc.get("last_name"),
                    dni=doc.get("dni"),
                    confidence=doc.get("confidence"),
                    duration_ms=doc["duration_ms"],
                    image_url=doc.get("image_url"),
                    used_at=doc["used_at"],
                )
                for doc in docs
            ),
            total,
        )
