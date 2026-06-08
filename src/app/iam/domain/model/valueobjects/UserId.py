from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID



@dataclass(frozen=True, slots=True)
class UserId:
    value: str

    def __post_init__(self) -> None:
        try:
            UUID(self.value)
        except ValueError as error:
            raise ValueError("user_id must be a valid UUID") from error
