from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.core.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class FaceRegisteredEvent:
    person_id: str
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.person_id or not self.person_id.strip():
            raise ValidationError("person_id cannot be empty")
