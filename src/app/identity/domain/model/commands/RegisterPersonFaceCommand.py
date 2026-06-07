from __future__ import annotations

from dataclasses import dataclass

from src.app.shared.exceptions import ValidationError
from src.app.identity.domain.model.valueobjects import PeruvianDni


@dataclass(frozen=True, slots=True)
class RegisterPersonFaceCommand:
    dni: str
    image_bytes: bytes
    image_filename: str | None = None
    image_content_type: str | None = None

    def __post_init__(self) -> None:
        PeruvianDni(self.dni)
        if not self.image_bytes:
            raise ValidationError("image_bytes cannot be empty")
        if self.image_filename is not None and not self.image_filename.strip():
            raise ValidationError("image_filename cannot be empty")
        if self.image_content_type is not None and not self.image_content_type.strip():
            raise ValidationError("image_content_type cannot be empty")
