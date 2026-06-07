from __future__ import annotations

from functools import lru_cache
from typing import Annotated, AsyncIterator

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
from src.app.identity.infrastructure.persistence.sqlalchemy import (
    SqlAlchemySessionFactory,
)
from src.app.identity.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemyPersonRepository,
    SqlAlchemyUsageLogRepository,
)
from src.app.shared.config import settings


@lru_cache(maxsize=1)
def _session_factory() -> SqlAlchemySessionFactory:
    return SqlAlchemySessionFactory(db_path=settings.db_path)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async for session in _session_factory().session():
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        break


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
    session: Annotated[AsyncSession, Depends(get_db_session)],
    extraction_service: Annotated[
        FaceEmbeddingExtractionService,
        Depends(get_face_embedding_extraction_acl_service),
    ],
) -> PersonIdentificationQueryServiceImpl:
    repository = SqlAlchemyPersonRepository(
        session=session,
        max_embeddings_per_person=settings.max_embeddings_per_person,
    )
    return PersonIdentificationQueryServiceImpl(
        person_repository=repository,
        extraction_query_service=extraction_service,
        match_threshold=settings.match_threshold,
    )


async def get_usage_log_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SqlAlchemyUsageLogRepository:
    return SqlAlchemyUsageLogRepository(session=session)


async def init_database() -> None:
    await _session_factory().init_models()
