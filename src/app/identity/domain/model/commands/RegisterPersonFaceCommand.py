from __future__ import annotations

from dataclasses import dataclass

from src.app.shared.exceptions import ValidationError
from src.app.identity.domain.model.valueobjects import PeruvianDni


@dataclass(frozen=True, slots=True)
class RegisterPersonFaceCommand:
    dni: str
    image_bytes: bytes

    def __post_init__(self) -> None:
        PeruvianDni(self.dni)
        if not self.image_bytes:
            raise ValidationError("image_bytes cannot be empty")
