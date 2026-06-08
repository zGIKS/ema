from __future__ import annotations

from src.app.identity.domain.model.entities import PersonAggregate
from src.app.identity.domain.model.queries import GetPersonByIdQuery
from src.app.identity.domain.model.queries import GetRegisteredPersonsQuery
from src.app.identity.domain.model.results import RegisteredPersonsPageResult
from src.app.identity.domain.repositories import PersonRepository
from src.app.identity.domain.services import PersonDirectoryQueryService


class PersonDirectoryQueryServiceImpl(PersonDirectoryQueryService):
    def __init__(self, *, person_repository: PersonRepository) -> None:
        self._person_repository = person_repository

    async def handle_get_person_by_id(
        self,
        query: GetPersonByIdQuery,
    ) -> PersonAggregate | None:
        return await self._person_repository.find_by_id(query.person_id)

    async def handle_get_registered_persons(
        self,
        query: GetRegisteredPersonsQuery,
    ) -> RegisteredPersonsPageResult:
        persons, total = await self._person_repository.find_paginated(
            page=query.page,
            page_size=query.page_size,
            search_term=query.search_term,
            dni=query.dni,
        )
        return RegisteredPersonsPageResult(
            items=persons,
            page=query.page,
            page_size=query.page_size,
            total=total,
        )
