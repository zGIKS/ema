from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.biometrics.application.internal.outboundservices.acl.FaceEmbeddingExtractionService import (
    FaceEmbeddingExtractionService,
)
from src.app.biometrics.application.internal.queryservices.PersonIdentificationQueryServiceImpl import (
    PersonIdentificationQueryServiceImpl,
)
from src.app.biometrics.domain.services import FaceEmbeddingExtractionQueryService
from src.app.biometrics.infrastructure.ai.insightface_engine import (
    InsightFaceRecognitionEngine,
)
from src.app.identity.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemyPersonRepository,
)
from src.app.auditory.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemyUsageLogRepository,
)
from src.app.shared.infrastructure.persistence.sqlalchemy import get_session
from src.app.shared.config import settings


async def get_database() -> AsyncIterator[AsyncSession]:
    async for session in get_session():
        yield session


def get_embedding_extraction_query_service() -> FaceEmbeddingExtractionQueryService:
    return InsightFaceRecognitionEngine(
        model_name=settings.insightface_model,
        det_size=settings.insightface_det_size,
    )


def get_face_embedding_extraction_acl_service(
    extraction_engine: Annotated[
        FaceEmbeddingExtractionQueryService,
        Depends(get_embedding_extraction_query_service),
    ],
) -> FaceEmbeddingExtractionService:
    return FaceEmbeddingExtractionService(engine=extraction_engine)


async def get_person_identification_query_service(
    database: Annotated[AsyncSession, Depends(get_database)],
    extraction_service: Annotated[
        FaceEmbeddingExtractionService,
        Depends(get_face_embedding_extraction_acl_service),
    ],
) -> PersonIdentificationQueryServiceImpl:
    repository = SqlAlchemyPersonRepository(
        database=database,
        max_embeddings_per_person=settings.max_embeddings_per_person,
    )
    return PersonIdentificationQueryServiceImpl(
        person_repository=repository,
        extraction_query_service=extraction_service,
        match_threshold=settings.match_threshold,
    )


async def get_usage_log_repository(
    database: Annotated[AsyncSession, Depends(get_database)],
) -> SqlAlchemyUsageLogRepository:
    return SqlAlchemyUsageLogRepository(session=database)
