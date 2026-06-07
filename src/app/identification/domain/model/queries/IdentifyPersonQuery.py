from __future__ import annotations

from dataclasses import dataclass

from src.shared.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class IdentifyPersonQuery:
    image_bytes: bytes

    def __post_init__(self) -> None:
        if not self.image_bytes:
            raise ValidationError("image_bytes cannot be empty")
