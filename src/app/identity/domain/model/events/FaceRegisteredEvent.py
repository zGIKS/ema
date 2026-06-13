from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.app.shared.validation import validate_uuid_string


@dataclass(frozen=True, slots=True)
class FaceRegisteredEvent:
    person_id: str
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        object.__setattr__(self, "person_id", validate_uuid_string(self.person_id, "person_id"))
