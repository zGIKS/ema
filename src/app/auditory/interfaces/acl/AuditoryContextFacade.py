from __future__ import annotations

from typing import Protocol


class AuditoryContextFacade(Protocol):
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
        ...

    async def log_register(
        self,
        *,
        person_id: str,
        first_name: str,
        last_name: str,
        dni: str,
        duration_ms: int,
        image_url: str | None = None,
    ) -> None:
        ...

    async def log_add_person_face_samples(
        self,
        *,
        person_id: str,
        first_name: str,
        last_name: str,
        dni: str,
        samples_added: int,
        total_samples: int,
        duration_ms: int,
    ) -> None:
        ...
