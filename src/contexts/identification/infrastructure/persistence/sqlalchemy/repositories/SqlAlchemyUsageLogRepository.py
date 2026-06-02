from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.contexts.identification.domain.repositories import UsageLogRepository
from src.contexts.identification.infrastructure.persistence.sqlalchemy.models.UsageLogModel import (
    UsageLogModel,
)


class SqlAlchemyUsageLogRepository(UsageLogRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def log_identify(
        self,
        *,
        person_id: str | None,
        confidence: float,
        duration_ms: int,
    ) -> None:
        self._session.add(
            UsageLogModel(
                operation="identify",
                person_id=person_id,
                confidence=float(confidence),
                duration_ms=int(duration_ms),
                used_at=int(datetime.now(UTC).timestamp()),
            )
        )
        await self._session.flush()

    async def log_register(self, *, person_id: str, duration_ms: int) -> None:
        self._session.add(
            UsageLogModel(
                operation="register",
                person_id=person_id,
                confidence=None,
                duration_ms=int(duration_ms),
                used_at=int(datetime.now(UTC).timestamp()),
            )
        )
        await self._session.flush()
