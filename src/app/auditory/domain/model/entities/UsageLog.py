from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UsageLog:
    operation: str
    person_id: str | None
    first_name: str | None
    last_name: str | None
    dni: str | None
    confidence: float | None
    samples_added: int | None
    total_samples: int | None
    duration_ms: int
    image_url: str | None
    used_at: int
