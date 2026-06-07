from __future__ import annotations

from src.app.identification.domain.model.results import FaceExtractionResult
from src.app.identification.domain.services import FaceEmbeddingExtractionQueryService


class FaceEmbeddingExtractionService(FaceEmbeddingExtractionQueryService):
    """
    ACL outbound service abstraction to keep application services
    decoupled from concrete extraction engines.
    """

    def __init__(self, engine: FaceEmbeddingExtractionQueryService) -> None:
        self._engine = engine

    async def handle_extract_embedding(self, image_bytes: bytes) -> FaceExtractionResult:
        return await self._engine.handle_extract_embedding(image_bytes)
