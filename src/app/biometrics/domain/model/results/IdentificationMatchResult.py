from __future__ import annotations

from dataclasses import dataclass

from src.app.biometrics.domain.model.valueobjects import (
    ConfidenceScore,
    SimilarityScore,
)
from src.app.identity.domain.model.valueobjects import PersonId


@dataclass(frozen=True, slots=True)
class IdentificationMatchResult:
    person_id: PersonId
    similarity: SimilarityScore
    confidence: ConfidenceScore
