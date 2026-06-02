from __future__ import annotations

from dataclasses import dataclass

from src.core.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class PersonId:
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValidationError("PersonId cannot be empty")
