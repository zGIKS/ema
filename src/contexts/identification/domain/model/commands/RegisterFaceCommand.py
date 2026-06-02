from __future__ import annotations

from dataclasses import dataclass

from src.core.exceptions import ValidationError
from src.contexts.identification.domain.model.valueobjects import PersonName, PeruvianDni


@dataclass(frozen=True, slots=True)
class RegisterFaceCommand:
    first_name: str
    last_name: str
    dni: str
    image_bytes: bytes

    def __post_init__(self) -> None:
        PersonName(self.first_name)
        PersonName(self.last_name)
        PeruvianDni(self.dni)
        if not self.image_bytes:
            raise ValidationError("image_bytes cannot be empty")
