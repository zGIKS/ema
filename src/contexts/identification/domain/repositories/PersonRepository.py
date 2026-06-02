from __future__ import annotations

from typing import Protocol

from src.contexts.identification.domain.model.entities import PersonAggregate
from src.contexts.identification.domain.model.results import IdentificationMatchResult
from src.contexts.identification.domain.model.valueobjects import (
    FaceEmbedding,
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
