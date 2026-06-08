from __future__ import annotations

from dataclasses import dataclass

from src.app.identity.domain.model.valueobjects import PersonId


@dataclass(frozen=True, slots=True)
class GetPersonByIdQuery:
    person_id: PersonId
