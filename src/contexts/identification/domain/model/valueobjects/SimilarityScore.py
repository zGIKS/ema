from __future__ import annotations

from dataclasses import dataclass

from src.core.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class SimilarityScore:
    value: float

    def __post_init__(self) -> None:
        numeric = float(self.value)
        if not (-1.0 <= numeric <= 1.0):
            raise ValidationError("SimilarityScore must be between -1 and 1")
