from __future__ import annotations

from dataclasses import dataclass

from src.app.iam.domain.model.valueobjects import UserId
from src.app.iam.domain.model.valueobjects import UserRole
from src.app.shared.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class UpdateUserRoleCommand:
    user_id: UserId
    role: UserRole

    def __post_init__(self) -> None:
        if not self.user_id.value.strip():
            raise ValidationError("user_id cannot be empty")
