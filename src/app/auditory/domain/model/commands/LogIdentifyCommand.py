from __future__ import annotations

from dataclasses import dataclass

from src.app.shared.exceptions import ValidationError
from src.app.shared.validation import validate_uuid_string


@dataclass(frozen=True, slots=True)
class LogIdentifyCommand:
    user_id: str
    person_id: str | None
    first_name: str | None
    last_name: str | None
    dni: str | None
    confidence: float | None
    duration_ms: int
    image_url: str | None

    def __post_init__(self) -> None:
        object.__setattr__(self, "user_id", validate_uuid_string(self.user_id, "user_id"))
        if self.person_id is not None:
            object.__setattr__(self, "person_id", validate_uuid_string(self.person_id, "person_id"))
        if self.duration_ms < 0:
            raise ValidationError("duration_ms cannot be negative")
