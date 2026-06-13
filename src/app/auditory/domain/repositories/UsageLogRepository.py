from __future__ import annotations

from typing import Protocol

from src.app.auditory.domain.model.entities.UsageLog import UsageLog


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
        ...

    async def find_paginated(
        self,
        *,
        page: int,
        page_size: int,
        user_id: str | None = None,
    ) -> tuple[tuple[UsageLog, ...], int]:
        ...
