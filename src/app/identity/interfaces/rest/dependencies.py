from __future__ import annotations

from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.identity.application.internal.commandservices.PersonEnrollmentCommandServiceImpl import (
    PersonEnrollmentCommandServiceImpl,
)
from src.app.identity.application.internal.outboundservices.acl.CloudinaryImageUploadService import (
    CloudinaryImageUploadService,
)
from src.app.identity.application.internal.outboundservices.acl.DecolectaDniLookupService import (
    DecolectaDniLookupService,
)
from src.app.biometrics.application.internal.outboundservices.acl.FaceEmbeddingExtractionService import (
    FaceEmbeddingExtractionService,
)
from src.app.biometrics.domain.services import FaceEmbeddingExtractionQueryService
from src.app.biometrics.infrastructure.ai.insightface_engine import (
    InsightFaceRecognitionEngine,
)
from src.app.identity.application.internal.queryservices.PersonDirectoryQueryServiceImpl import (
    PersonDirectoryQueryServiceImpl,
)
from src.app.identity.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemyPersonRepository,
)
from src.app.auditory.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemyUsageLogRepository,
)
from src.app.shared.config import settings
from src.app.shared.infrastructure.persistence.sqlalchemy import get_session


async def get_database() -> AsyncIterator[AsyncSession]:
    async for session in get_session():
        yield session


def get_embedding_extraction_query_service() -> FaceEmbeddingExtractionQueryService:
    engine_setting = settings.engine.strip().lower()
    if engine_setting != "insightface":
        raise ValueError("FR_ENGINE must be set to insightface")

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


def get_dni_lookup_query_service() -> DecolectaDniLookupService:
    return DecolectaDniLookupService(
        api_key=settings.decolecta_api_key,
        base_url=settings.decolecta_base_url,
    )


@lru_cache(maxsize=1)
def get_cloudinary_image_upload_service() -> CloudinaryImageUploadService:
    return CloudinaryImageUploadService(
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        cloud_name=settings.cloudinary_cloud_name,
    )


async def get_person_enrollment_command_service(
    database: Annotated[AsyncSession, Depends(get_database)],
    extraction_service: Annotated[
        FaceEmbeddingExtractionService,
        Depends(get_face_embedding_extraction_acl_service),
    ],
    image_upload_service: Annotated[
        CloudinaryImageUploadService,
        Depends(get_cloudinary_image_upload_service),
    ],
    dni_lookup_service: Annotated[
        DecolectaDniLookupService,
        Depends(get_dni_lookup_query_service),
    ],
) -> PersonEnrollmentCommandServiceImpl:
    repository = SqlAlchemyPersonRepository(
        session=database,
        max_embeddings_per_person=settings.max_embeddings_per_person,
    )
    return PersonEnrollmentCommandServiceImpl(
        person_repository=repository,
        extraction_query_service=extraction_service,
        image_upload_service=image_upload_service,
        dni_lookup_query_service=dni_lookup_service,
        max_embeddings_per_person=settings.max_embeddings_per_person,
        match_threshold=settings.match_threshold,
    )


async def get_person_directory_query_service(
    database: Annotated[AsyncSession, Depends(get_database)],
) -> PersonDirectoryQueryServiceImpl:
    repository = SqlAlchemyPersonRepository(
        session=database,
        max_embeddings_per_person=settings.max_embeddings_per_person,
    )
    return PersonDirectoryQueryServiceImpl(person_repository=repository)


async def get_usage_log_repository(
    database: Annotated[AsyncSession, Depends(get_database)],
) -> SqlAlchemyUsageLogRepository:
    return SqlAlchemyUsageLogRepository(session=database)


from src.app.identity.application.internal.queryservices.UsageLogQueryServiceImpl import (
    UsageLogQueryServiceImpl,
)


async def get_usage_log_query_service(
    usage_log_repository: Annotated[
        SqlAlchemyUsageLogRepository,
        Depends(get_usage_log_repository),
    ],
) -> UsageLogQueryServiceImpl:
    return UsageLogQueryServiceImpl(usage_log_repository=usage_log_repository)
