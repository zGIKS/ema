from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LogAddPersonFaceSamplesCommand:
    user_id: str
    person_id: str
    first_name: str
    last_name: str
    dni: str
    samples_added: int
    total_samples: int
    duration_ms: int

    def __post_init__(self) -> None:
        if not self.person_id.strip():
            raise ValueError("person_id cannot be empty")
        if not self.first_name.strip():
            raise ValueError("first_name cannot be empty")
        if not self.last_name.strip():
            raise ValueError("last_name cannot be empty")
        if not self.dni.strip():
            raise ValueError("dni cannot be empty")
        if self.samples_added <= 0:
            raise ValueError("samples_added must be greater than zero")
        if self.total_samples <= 0:
            raise ValueError("total_samples must be greater than zero")
        if self.duration_ms < 0:
            raise ValueError("duration_ms cannot be negative")
