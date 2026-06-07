from __future__ import annotations

from dataclasses import dataclass

from src.app.identity.domain.model.valueobjects import PersonName, PeruvianDni


@dataclass(frozen=True, slots=True)
class DniLookupResult:
    document_number: str
    first_name: str
    first_last_name: str
    second_last_name: str
    full_name: str

    def __post_init__(self) -> None:
        PeruvianDni(self.document_number)
        PersonName(self.first_name)
        PersonName(self.first_last_name)
        if self.second_last_name.strip():
            PersonName(self.second_last_name)
