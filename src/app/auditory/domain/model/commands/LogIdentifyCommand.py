from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LogIdentifyCommand:
    person_id: str | None
    first_name: str | None
    last_name: str | None
    dni: str | None
    confidence: float | None
    duration_ms: int
    image_url: str | None
