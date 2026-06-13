from __future__ import annotations

from dataclasses import dataclass

from src.app.shared.exceptions import ValidationError
from src.app.shared.validation import validate_uuid_string


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
        object.__setattr__(self, "user_id", validate_uuid_string(self.user_id, "user_id"))
        object.__setattr__(self, "person_id", validate_uuid_string(self.person_id, "person_id"))
        if not self.first_name.strip():
            raise ValidationError("first_name cannot be empty")
        if not self.last_name.strip():
            raise ValidationError("last_name cannot be empty")
        if not self.dni.strip():
            raise ValidationError("dni cannot be empty")
        if self.samples_added <= 0:
            raise ValidationError("samples_added must be greater than zero")
        if self.total_samples <= 0:
            raise ValidationError("total_samples must be greater than zero")
        if self.duration_ms < 0:
            raise ValidationError("duration_ms cannot be negative")
