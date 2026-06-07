from __future__ import annotations

from src.app.identification.domain.model.queries import GetRegisteredPersonsQuery
from src.app.identification.domain.model.results import RegisteredPersonsPageResult
from src.app.identification.domain.repositories import PersonRepository
from src.app.identification.domain.services import PersonDirectoryQueryService


class PersonDirectoryQueryServiceImpl(PersonDirectoryQueryService):
    def __init__(self, *, person_repository: PersonRepository) -> None:
        self._person_repository = person_repository

    async def handle_get_registered_persons(
        self,
        query: GetRegisteredPersonsQuery,
    ) -> RegisteredPersonsPageResult:
        persons, total = await self._person_repository.find_paginated(
            page=query.page,
            page_size=query.page_size,
        )
        return RegisteredPersonsPageResult(
            items=persons,
            page=query.page,
            page_size=query.page_size,
            total=total,
        )
