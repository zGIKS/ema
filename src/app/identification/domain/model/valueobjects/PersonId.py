from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from src.app.shared.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class PersonId:
    value: str

    def __post_init__(self) -> None:
        normalized = (self.value or "").strip()
        if not normalized:
            raise ValidationError("PersonId cannot be empty")
        try:
            UUID(normalized)
        except ValueError as error:
            raise ValidationError("PersonId must be a valid UUID") from error
