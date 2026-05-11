from __future__ import annotations

from dataclasses import dataclass

from src.core.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class PersonId:
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValidationError("PersonId cannot be empty")


@dataclass(frozen=True, slots=True)
class FaceEmbedding:
    """
    Domain-friendly representation for a face embedding.
    Keep it a plain list of floats to avoid leaking numpy/torch tensors upward.
    """

    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.values) == 0:
            raise ValidationError("FaceEmbedding cannot be empty")
        # Basic sanity: no NaNs/inf, values are floats.
        for v in self.values:
            if not isinstance(v, (float, int)):
                raise ValidationError("FaceEmbedding values must be numeric")
            if v != v:  # NaN check
                raise ValidationError("FaceEmbedding cannot contain NaN")


@dataclass(frozen=True, slots=True)
class BoundingBox:
    x: int
    y: int
    w: int
    h: int

    def __post_init__(self) -> None:
        if self.x < 0 or self.y < 0:
            raise ValidationError("BoundingBox x/y must be >= 0")
        if self.w <= 0 or self.h <= 0:
            raise ValidationError("BoundingBox w/h must be > 0")


@dataclass(frozen=True, slots=True)
class ConfidenceScore:
    value: float

    def __post_init__(self) -> None:
        if not (0.0 <= float(self.value) <= 1.0):
            raise ValidationError("ConfidenceScore must be between 0 and 1")

