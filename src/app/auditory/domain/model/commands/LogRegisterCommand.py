from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LogRegisterCommand:
    person_id: str
    duration_ms: int
