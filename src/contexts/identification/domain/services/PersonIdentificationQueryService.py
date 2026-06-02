from __future__ import annotations

from typing import Protocol

from src.contexts.identification.domain.model.queries import IdentifyPersonQuery
from src.contexts.identification.domain.model.results import IdentificationResult


class PersonIdentificationQueryService(Protocol):
    async def handle_identify_person(self, query: IdentifyPersonQuery) -> IdentificationResult:
        ...
