from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LogRegisterCommand:
    person_id: str
    first_name: str
    last_name: str
    dni: str
    duration_ms: int
