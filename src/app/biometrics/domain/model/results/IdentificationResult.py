from __future__ import annotations

from dataclasses import dataclass

from src.app.biometrics.domain.model.valueobjects import BoundingBox, ConfidenceScore
from src.app.identity.domain.model.valueobjects import PersonId


@dataclass(frozen=True, slots=True)
class IdentificationResult:
    person_id: PersonId | None
    first_name: str | None
    last_name: str | None
    dni: str | None
    image_url: str | None
    confidence: ConfidenceScore
    box: BoundingBox | None
