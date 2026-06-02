from __future__ import annotations

from dataclasses import dataclass

from src.core.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class ConfidenceScore:
    value: float

    def __post_init__(self) -> None:
        numeric = float(self.value)
        if not (0.0 <= numeric <= 1.0):
            raise ValidationError("ConfidenceScore must be between 0 and 1")
