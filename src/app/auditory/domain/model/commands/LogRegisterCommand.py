from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LogRegisterCommand:
    user_id: str
    person_id: str
    first_name: str
    last_name: str
    dni: str
    duration_ms: int
    image_url: str | None = None
