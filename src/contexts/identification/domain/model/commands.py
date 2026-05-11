from __future__ import annotations

from dataclasses import dataclass

from src.core.exceptions import ValidationError
from src.contexts.identification.domain.model.valueobjects import PersonId


@dataclass(frozen=True, slots=True)
class IdentifyPersonCommand:
    image_bytes: bytes

    def __post_init__(self) -> None:
        if not self.image_bytes:
            raise ValidationError("image_bytes cannot be empty")


@dataclass(frozen=True, slots=True)
class RegisterFaceCommand:
    person_id: str
    image_bytes: bytes

    def __post_init__(self) -> None:
        # Convert here for consistent validation behavior, but keep field as str
        # to make external mapping explicit at handler boundaries.
        PersonId(self.person_id)
        if not self.image_bytes:
            raise ValidationError("image_bytes cannot be empty")

