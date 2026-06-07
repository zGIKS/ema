from __future__ import annotations

from typing import Protocol

from src.app.identification.domain.model.results import FaceExtractionResult


class FaceEmbeddingExtractionQueryService(Protocol):
    async def handle_extract_embedding(self, image_bytes: bytes) -> FaceExtractionResult:
        ...
