from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UsageLog:
    user_id: str | None
    operation: str
    person_id: str | None
    confidence: float | None
    duration_ms: int
    image_url: str | None
    used_at: int
