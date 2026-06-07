from __future__ import annotations

from dataclasses import dataclass

from src.app.identification.domain.model.valueobjects import BoundingBox, ConfidenceScore, PersonId


@dataclass(frozen=True, slots=True)
class IdentificationResult:
    person_id: PersonId | None
    first_name: str | None
    last_name: str | None
    dni: str | None
    photo: str | None
    confidence: ConfidenceScore
    box: BoundingBox | None
