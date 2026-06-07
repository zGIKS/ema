from __future__ import annotations

from dataclasses import dataclass

from src.app.biometrics.domain.model.valueobjects import FaceEmbedding


@dataclass(frozen=True, slots=True)
class FaceSample:
    embedding: FaceEmbedding
