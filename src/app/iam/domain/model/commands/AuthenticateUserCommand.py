from __future__ import annotations

from dataclasses import dataclass
import re

from src.app.shared.exceptions import ValidationError


_USERNAME_PATTERN = re.compile(r"^U\d{9}$")


@dataclass(frozen=True, slots=True)
class AuthenticateUserCommand:
    username: str
    password: str

    def __post_init__(self) -> None:
        if not _USERNAME_PATTERN.fullmatch(self.username):
            raise ValidationError("username must match U#########")
        if not self.password:
            raise ValidationError("password cannot be empty")
