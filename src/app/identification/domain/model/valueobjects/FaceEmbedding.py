from __future__ import annotations

from dataclasses import dataclass

from src.app.shared.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class FaceEmbedding:
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.values) == 0:
            raise ValidationError("FaceEmbedding cannot be empty")

        for value in self.values:
            if not isinstance(value, (float, int)):
                raise ValidationError("FaceEmbedding values must be numeric")
            if value != value:
                raise ValidationError("FaceEmbedding cannot contain NaN")
