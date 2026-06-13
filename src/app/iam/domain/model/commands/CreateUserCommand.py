from __future__ import annotations

from dataclasses import dataclass

from src.app.shared.exceptions import ValidationError
from src.app.shared.validation import USERNAME_REGEX


@dataclass(frozen=True, slots=True)
class CreateUserCommand:
    username: str
    password: str

    def __post_init__(self) -> None:
        normalized_username = self.username.strip().lower()
        if not normalized_username:
            raise ValidationError("username cannot be empty")
        if not USERNAME_REGEX.fullmatch(normalized_username):
            raise ValidationError("username must contain only letters and be 3 to 30 characters long")
        object.__setattr__(self, "username", normalized_username)
        if len(self.password) < 12:
            raise ValidationError("password must be at least 12 characters long")
        if not any(ch.islower() for ch in self.password):
            raise ValidationError("password must include a lowercase letter")
        if not any(ch.isupper() for ch in self.password):
            raise ValidationError("password must include an uppercase letter")
        if not any(ch.isdigit() for ch in self.password):
            raise ValidationError("password must include a digit")
        if not any(not ch.isalnum() for ch in self.password):
            raise ValidationError("password must include a symbol")
