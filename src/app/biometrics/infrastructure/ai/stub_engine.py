from __future__ import annotations

import hashlib

import numpy as np

from src.app.biometrics.domain.model.results import FaceExtractionResult
from src.app.biometrics.domain.model.valueobjects import BoundingBox, FaceEmbedding
from src.app.biometrics.domain.services import FaceEmbeddingExtractionQueryService


class StubFaceRecognitionEngine(FaceEmbeddingExtractionQueryService):
    """
    Deterministic "fake" embedding extractor.

    Useful to validate architecture + flows without shipping heavy ML deps.
    Replace with a real adapter (InsightFace/ArcFace/etc) later.
    """

    def __init__(self, embedding_dim: int = 128) -> None:
        self._dim = int(embedding_dim)

    async def handle_extract_embedding(self, image_bytes: bytes) -> FaceExtractionResult:
        digest = hashlib.sha256(image_bytes).digest()
        seed = int.from_bytes(digest[:8], "big", signed=False)
        rng = np.random.default_rng(seed)
        vec = rng.normal(0, 1, size=(self._dim,)).astype(np.float32)
        vec /= max(1e-6, float(np.linalg.norm(vec)))

        # Fake a box to keep API shape stable.
        box = BoundingBox(x=0, y=0, w=1, h=1)
        return FaceExtractionResult(
            embedding=FaceEmbedding(tuple(float(x) for x in vec.tolist())),
            box=box,
        )
