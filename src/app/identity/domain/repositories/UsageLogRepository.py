from typing import Protocol
from src.app.identity.domain.model.entities.UsageLog import UsageLog


class UsageLogRepository(Protocol):
    async def log_identify(
        self,
        *,
        user_id: str,
        person_id: str | None,
        confidence: float | None,
        duration_ms: int,
        image_url: str | None = None,
    ) -> None:
        ...

    async def log_register(
        self,
        *,
        user_id: str,
        person_id: str,
        duration_ms: int,
        image_url: str | None = None,
    ) -> None:
        ...

    async def find_paginated(
        self,
        *,
        page: int,
        page_size: int,
        user_id: str | None = None,
    ) -> tuple[tuple[UsageLog, ...], int]:
        ...
