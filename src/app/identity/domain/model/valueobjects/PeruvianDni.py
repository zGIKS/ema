from __future__ import annotations

from dataclasses import dataclass

from src.app.shared.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class PeruvianDni:
    value: str

    def __post_init__(self) -> None:
        normalized = (self.value or "").strip()
        if len(normalized) != 8 or not normalized.isdigit():
            raise ValidationError("DNI peruano debe tener exactamente 8 digitos")
