from __future__ import annotations

from dataclasses import dataclass

from src.app.identification.domain.model.entities import PersonAggregate


@dataclass(frozen=True, slots=True)
class RegisteredPersonsPageResult:
    items: tuple[PersonAggregate, ...]
    page: int
    page_size: int
    total: int
