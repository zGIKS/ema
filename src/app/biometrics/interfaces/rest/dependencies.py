from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

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
from src.app.identity.infrastructure.persistence.mongodb.MongoDbClientFactory import (
    MongoDbClientFactory,
)
from src.app.identity.infrastructure.persistence.mongodb.repositories.MongoDbPersonRepository import (
    MongoDbPersonRepository,
)
from src.app.identity.infrastructure.persistence.mongodb.repositories.MongoDbUsageLogRepository import (
    MongoDbUsageLogRepository,
)
from src.app.shared.config import settings


@lru_cache(maxsize=1)
def _client_factory() -> MongoDbClientFactory:
    return MongoDbClientFactory(db_url=settings.db_url, db_name=settings.db_name)


async def get_database() -> AsyncIOMotorDatabase:
    return _client_factory().database()


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
    database: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
    extraction_service: Annotated[
        FaceEmbeddingExtractionService,
        Depends(get_face_embedding_extraction_acl_service),
    ],
) -> PersonIdentificationQueryServiceImpl:
    repository = MongoDbPersonRepository(
        database=database,
        max_embeddings_per_person=settings.max_embeddings_per_person,
    )
    return PersonIdentificationQueryServiceImpl(
        person_repository=repository,
        extraction_query_service=extraction_service,
        match_threshold=settings.match_threshold,
    )


async def get_usage_log_repository(
    database: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> MongoDbUsageLogRepository:
    return MongoDbUsageLogRepository(database=database)


async def init_database() -> None:
    await _client_factory().init_database()
