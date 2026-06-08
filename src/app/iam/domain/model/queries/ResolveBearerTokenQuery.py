from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResolveBearerTokenQuery:
    token: str

    def __post_init__(self) -> None:
        if not self.token.strip():
            raise ValueError("token cannot be empty")
