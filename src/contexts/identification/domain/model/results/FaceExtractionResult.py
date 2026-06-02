from __future__ import annotations

from dataclasses import dataclass

from src.contexts.identification.domain.model.valueobjects import BoundingBox, FaceEmbedding


@dataclass(frozen=True, slots=True)
class FaceExtractionResult:
    embedding: FaceEmbedding
    box: BoundingBox | None
