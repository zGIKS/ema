from __future__ import annotations

from typing import Protocol

from src.app.identification.domain.model.queries import GetRegisteredPersonsQuery
from src.app.identification.domain.model.results import RegisteredPersonsPageResult


class PersonDirectoryQueryService(Protocol):
    async def handle_get_registered_persons(
        self,
        query: GetRegisteredPersonsQuery,
    ) -> RegisteredPersonsPageResult:
        ...
