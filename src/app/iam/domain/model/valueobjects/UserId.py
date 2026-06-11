from __future__ import annotations

from dataclasses import dataclass

from src.app.shared.validation import validate_uuid_string


@dataclass(frozen=True, slots=True)
class UserId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", validate_uuid_string(self.value, "user_id"))
