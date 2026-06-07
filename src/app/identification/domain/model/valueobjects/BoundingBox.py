from __future__ import annotations

from dataclasses import dataclass

from src.shared.exceptions import ValidationError


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
