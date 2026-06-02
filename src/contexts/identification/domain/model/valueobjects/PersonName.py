from __future__ import annotations

from dataclasses import dataclass
import re

from src.core.exceptions import ValidationError

_SPANISH_NAME_RE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?: [A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*$")


@dataclass(frozen=True, slots=True)
class PersonName:
    value: str

    def __post_init__(self) -> None:
        normalized = " ".join((self.value or "").strip().split())
        if not normalized:
            raise ValidationError("Nombre/apellido no puede estar vacio")
        if len(normalized) > 80:
            raise ValidationError("Nombre/apellido no puede exceder 80 caracteres")
        if _SPANISH_NAME_RE.fullmatch(normalized) is None:
            raise ValidationError(
                "Nombre/apellido solo puede contener letras espanolas, espacios, enie y tildes"
            )
