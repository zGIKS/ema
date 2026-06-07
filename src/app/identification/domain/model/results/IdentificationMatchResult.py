from __future__ import annotations

from dataclasses import dataclass

from src.app.identification.domain.model.valueobjects import (
    ConfidenceScore,
    PersonId,
    SimilarityScore,
)


@dataclass(frozen=True, slots=True)
class IdentificationMatchResult:
    person_id: PersonId
    similarity: SimilarityScore
    confidence: ConfidenceScore
