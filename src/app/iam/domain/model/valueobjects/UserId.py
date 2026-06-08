from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("user_id cannot be empty")
