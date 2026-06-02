from __future__ import annotations

from dataclasses import dataclass

from src.core.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class GetRegisteredPersonsQuery:
    page: int = 1
    page_size: int = 20

    def __post_init__(self) -> None:
        if self.page <= 0:
            raise ValidationError("page must be greater than zero")

        if not 1 <= self.page_size <= 100:
            raise ValidationError("page_size must be between 1 and 100")
