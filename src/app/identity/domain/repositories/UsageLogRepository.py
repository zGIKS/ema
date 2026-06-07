from __future__ import annotations

from typing import Protocol


class UsageLogRepository(Protocol):
    async def log_identify(
        self,
        *,
        person_id: str | None,
        confidence: float,
        duration_ms: int,
    ) -> None:
        ...

    async def log_register(self, *, person_id: str, duration_ms: int) -> None:
        ...
