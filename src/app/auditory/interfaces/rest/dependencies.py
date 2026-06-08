from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.app.auditory.application.internal.commandservices.UsageLogCommandServiceImpl import (
    UsageLogCommandServiceImpl,
)
from src.app.auditory.application.internal.queryservices.UsageLogQueryServiceImpl import (
    UsageLogQueryServiceImpl,
)
from src.app.auditory.application.acl.AuditoryContextFacadeImpl import (
    AuditoryContextFacadeImpl,
)
from src.app.auditory.infrastructure.persistence.mongodb.repositories.MongoDbUsageLogRepository import (
    MongoDbUsageLogRepository,
)
from src.app.identity.infrastructure.persistence.mongodb.MongoDbClientFactory import (
    MongoDbClientFactory,
)
from src.app.shared.config import settings


@lru_cache(maxsize=1)
def _client_factory() -> MongoDbClientFactory:
    return MongoDbClientFactory(db_url=settings.db_url, db_name=settings.db_name)


async def get_database() -> AsyncIOMotorDatabase:
    return _client_factory().database()


async def get_usage_log_repository(
    database: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> MongoDbUsageLogRepository:
    return MongoDbUsageLogRepository(database=database)


async def get_usage_log_command_service(
    repository: Annotated[
        MongoDbUsageLogRepository,
        Depends(get_usage_log_repository),
    ],
) -> UsageLogCommandServiceImpl:
    return UsageLogCommandServiceImpl(usage_log_repository=repository)


async def get_usage_log_query_service(
    repository: Annotated[
        MongoDbUsageLogRepository,
        Depends(get_usage_log_repository),
    ],
) -> UsageLogQueryServiceImpl:
    return UsageLogQueryServiceImpl(usage_log_repository=repository)


async def get_auditory_context_facade(
    command_service: Annotated[
        UsageLogCommandServiceImpl,
        Depends(get_usage_log_command_service),
    ],
) -> AuditoryContextFacadeImpl:
    return AuditoryContextFacadeImpl(command_service=command_service)
