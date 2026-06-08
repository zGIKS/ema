from __future__ import annotations

from typing import Protocol

from src.app.identity.domain.model.entities import PersonAggregate
from src.app.identity.domain.model.queries import GetPersonByIdQuery
from src.app.identity.domain.model.queries import GetRegisteredPersonsQuery
from src.app.identity.domain.model.results import RegisteredPersonsPageResult


class PersonDirectoryQueryService(Protocol):
    async def handle_get_person_by_id(
        self,
        query: GetPersonByIdQuery,
    ) -> PersonAggregate | None:
        ...

    async def handle_get_registered_persons(
        self,
        query: GetRegisteredPersonsQuery,
    ) -> RegisteredPersonsPageResult:
        ...
