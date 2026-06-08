from __future__ import annotations

from dataclasses import dataclass
import re

from src.app.iam.domain.model.valueobjects import UserRole
from src.app.shared.exceptions import ValidationError


_USERNAME_PATTERN = re.compile(r"^U\d{9}$")


@dataclass(frozen=True, slots=True)
class CreateUserCommand:
    username: str
    password: str
    role: UserRole

    def __post_init__(self) -> None:
        if not _USERNAME_PATTERN.fullmatch(self.username):
            raise ValidationError("username must match U#########")
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
