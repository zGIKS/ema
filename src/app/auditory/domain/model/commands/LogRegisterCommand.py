from __future__ import annotations

from dataclasses import dataclass

from src.app.shared.exceptions import ValidationError
from src.app.shared.validation import validate_uuid_string


@dataclass(frozen=True, slots=True)
class LogRegisterCommand:
    user_id: str
    person_id: str
    first_name: str
    last_name: str
    dni: str
    duration_ms: int
    image_url: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "user_id", validate_uuid_string(self.user_id, "user_id"))
        object.__setattr__(self, "person_id", validate_uuid_string(self.person_id, "person_id"))
        if not self.first_name.strip():
            raise ValidationError("first_name cannot be empty")
        if not self.last_name.strip():
            raise ValidationError("last_name cannot be empty")
        if not self.dni.strip():
            raise ValidationError("dni cannot be empty")
        if self.duration_ms < 0:
            raise ValidationError("duration_ms cannot be negative")
