from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.app.shared.validation import validate_uuid_string


@dataclass(frozen=True, slots=True)
class UsageLog:
    user_id: str | None
    operation: str
    person_id: str | None
    confidence: float | None
    duration_ms: int
    image_url: str | None
    used_at: datetime

    def __post_init__(self) -> None:
        if self.user_id is not None:
            object.__setattr__(self, "user_id", validate_uuid_string(self.user_id, "user_id"))
        if self.person_id is not None:
            object.__setattr__(self, "person_id", validate_uuid_string(self.person_id, "person_id"))
