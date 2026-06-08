from typing import Protocol
from src.app.identity.domain.model.entities.UsageLog import UsageLog


class UsageLogRepository(Protocol):
    async def log_identify(
        self,
        *,
        person_id: str | None,
        confidence: float | None,
        duration_ms: int,
        image_url: str | None = None,
    ) -> None:
        ...

    async def log_register(self, *, person_id: str, duration_ms: int) -> None:
        ...

    async def find_paginated(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[tuple[UsageLog, ...], int]:
        ...
