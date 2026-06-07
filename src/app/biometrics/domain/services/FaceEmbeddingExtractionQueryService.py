from __future__ import annotations

from typing import Protocol

from src.app.biometrics.domain.model.results import FaceExtractionResult


class FaceEmbeddingExtractionQueryService(Protocol):
    async def handle_extract_embedding(self, image_bytes: bytes) -> FaceExtractionResult:
        ...
