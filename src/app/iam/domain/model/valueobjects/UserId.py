from __future__ import annotations

from dataclasses import dataclass
import re


_USER_ID_PATTERN = re.compile(r"^U\d{9}$")


@dataclass(frozen=True, slots=True)
class UserId:
    value: str

    def __post_init__(self) -> None:
        if not _USER_ID_PATTERN.fullmatch(self.value):
            raise ValueError("user_id must match U#########")
