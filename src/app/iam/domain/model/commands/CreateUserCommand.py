from __future__ import annotations

from dataclasses import dataclass

from src.app.iam.domain.model.valueobjects import UserRole
from src.app.shared.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class CreateUserCommand:
    username: str
    password: str
    role: UserRole

    def __post_init__(self) -> None:
        if not self.username.strip():
            raise ValidationError("username cannot be empty")
        if not self.password:
            raise ValidationError("password cannot be empty")
