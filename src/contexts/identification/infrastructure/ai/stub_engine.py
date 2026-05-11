from __future__ import annotations

import hashlib

import numpy as np

from src.contexts.identification.domain.model.valueobjects import BoundingBox
from src.contexts.identification.domain.services.face_recognition_service import (
    ExtractionResult,
    FaceRecognitionService,
)
from src.contexts.identification.infrastructure.acl.mappers import numpy_embedding_to_vo


class StubFaceRecognitionEngine(FaceRecognitionService):
    """
    Deterministic "fake" embedding extractor.

    Useful to validate architecture + flows without shipping heavy ML deps.
    Replace with a real adapter (InsightFace/ArcFace/etc) later.
    """

    def __init__(self, embedding_dim: int = 128) -> None:
        self._dim = int(embedding_dim)

    def extract(self, image_bytes: bytes) -> ExtractionResult:
        digest = hashlib.sha256(image_bytes).digest()
        seed = int.from_bytes(digest[:8], "big", signed=False)
        rng = np.random.default_rng(seed)
        vec = rng.normal(0, 1, size=(self._dim,)).astype(np.float32)
        vec /= max(1e-6, float(np.linalg.norm(vec)))

        # Fake a box to keep API shape stable.
        box = BoundingBox(x=0, y=0, w=1, h=1)
        return ExtractionResult(embedding=numpy_embedding_to_vo(vec), box=box)

