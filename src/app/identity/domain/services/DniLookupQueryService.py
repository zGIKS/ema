from __future__ import annotations

from typing import Protocol

from src.app.identity.domain.model.results import DniLookupResult
from src.app.identity.domain.model.valueobjects import PeruvianDni


class DniLookupQueryService(Protocol):
    async def handle_lookup_dni(self, dni: PeruvianDni) -> DniLookupResult | None:
        ...
