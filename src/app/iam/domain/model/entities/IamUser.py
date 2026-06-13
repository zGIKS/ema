from __future__ import annotations

from dataclasses import dataclass

from src.app.iam.domain.model.valueobjects import UserId, UserRole


@dataclass(frozen=True, slots=True)
class IamUser:
    user_id: UserId
    username: str
    password_hash: str
    role: UserRole
    is_active: bool
