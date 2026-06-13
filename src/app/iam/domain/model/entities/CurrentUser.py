from __future__ import annotations

from dataclasses import dataclass

from src.app.iam.domain.model.valueobjects import UserId, UserRole


@dataclass(frozen=True, slots=True)
class CurrentUser:
    user_id: UserId
    username: str
    role: UserRole

    @property
    def is_admin(self) -> bool:
        return self.role is UserRole.ADMIN
