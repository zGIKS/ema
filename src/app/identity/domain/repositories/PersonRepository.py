from __future__ import annotations

from typing import Protocol

from src.app.biometrics.domain.model.valueobjects import FaceEmbedding
from src.app.identity.domain.model.entities import PersonAggregate
from src.app.biometrics.domain.model.results import IdentificationMatchResult
from src.app.identity.domain.model.valueobjects import (
    PersonId,
    PeruvianDni,
)


class PersonRepository(Protocol):
    async def find_by_id(self, person_id: PersonId) -> PersonAggregate | None:
        ...

    async def find_by_dni(self, dni: PeruvianDni) -> PersonAggregate | None:
        ...

    async def save(self, person: PersonAggregate) -> PersonAggregate:
        ...

    async def find_best_match(self, embedding: FaceEmbedding) -> IdentificationMatchResult | None:
        ...

    async def find_paginated(
        self,
        *,
        page: int,
        page_size: int,
        search_term: str | None = None,
        dni: str | None = None,
    ) -> tuple[tuple[PersonAggregate, ...], int]:
        ...
