from __future__ import annotations

from dataclasses import dataclass

from src.app.shared.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class LogoutSessionCommand:
    refresh_token: str

    def __post_init__(self) -> None:
        if not self.refresh_token.strip():
            raise ValidationError("refresh_token cannot be empty")
