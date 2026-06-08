from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

    @classmethod
    def from_value(cls, value: str) -> "UserRole":
        normalized = value.strip().lower()
        for role in cls:
            if role.value == normalized:
                return role
        raise ValueError("Unsupported user role")
