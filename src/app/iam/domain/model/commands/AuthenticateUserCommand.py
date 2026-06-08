from __future__ import annotations

from dataclasses import dataclass

from src.app.shared.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class AuthenticateUserCommand:
    username: str
    password: str

    def __post_init__(self) -> None:
        if not self.username.strip():
            raise ValidationError("username cannot be empty")
        if not self.password:
            raise ValidationError("password cannot be empty")
