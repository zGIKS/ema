from __future__ import annotations

from dataclasses import dataclass

from src.app.shared.exceptions import ValidationError
from src.app.shared.validation import USERNAME_REGEX


@dataclass(frozen=True, slots=True)
class AuthenticateUserCommand:
    username: str
    password: str

    def __post_init__(self) -> None:
        normalized_username = self.username.strip().lower()
        if not normalized_username:
            raise ValidationError("username cannot be empty")
        if not USERNAME_REGEX.fullmatch(normalized_username):
            raise ValidationError("username must contain only letters and be 3 to 30 characters long")
        object.__setattr__(self, "username", normalized_username)
        if not self.password:
            raise ValidationError("password cannot be empty")
