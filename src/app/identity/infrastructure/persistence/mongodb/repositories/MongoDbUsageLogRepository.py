from __future__ import annotations

from datetime import UTC, datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.app.identity.domain.repositories import UsageLogRepository

class MongoDbUsageLogRepository(UsageLogRepository):
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self._collection = database.usage_logs

    async def log_identify(
        self,
        *,
        person_id: str | None,
        confidence: float,
        duration_ms: int,
    ) -> None:
        await self._collection.insert_one(
            {
                "operation": "identify",
                "person_id": person_id,
                "confidence": float(confidence),
                "duration_ms": int(duration_ms),
                "used_at": int(datetime.now(UTC).timestamp()),
            }
        )

    async def log_register(self, *, person_id: str, duration_ms: int) -> None:
        await self._collection.insert_one(
            {
                "operation": "register",
                "person_id": person_id,
                "confidence": None,
                "duration_ms": int(duration_ms),
                "used_at": int(datetime.now(UTC).timestamp()),
            }
        )
