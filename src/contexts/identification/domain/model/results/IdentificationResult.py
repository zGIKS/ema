from __future__ import annotations

from dataclasses import dataclass

from src.contexts.identification.domain.model.valueobjects import BoundingBox, ConfidenceScore, PersonId


@dataclass(frozen=True, slots=True)
class IdentificationResult:
    person_id: PersonId | None
    confidence: ConfidenceScore
    box: BoundingBox | None
