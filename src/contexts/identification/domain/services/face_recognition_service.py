from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.contexts.identification.domain.model.valueobjects import BoundingBox, FaceEmbedding


@dataclass(frozen=True, slots=True)
class ExtractionResult:
    embedding: FaceEmbedding
    box: BoundingBox | None


class FaceRecognitionService(Protocol):
    """
    Domain contract. Implementations live in infrastructure.
    """

    def extract(self, image_bytes: bytes) -> ExtractionResult: ...

