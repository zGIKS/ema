from __future__ import annotations

from dataclasses import dataclass

from src.app.shared.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class ResolveBearerTokenQuery:
    token: str

    def __post_init__(self) -> None:
        if not self.token.strip():
            raise ValidationError("token cannot be empty")
