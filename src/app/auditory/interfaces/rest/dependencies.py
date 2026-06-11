from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.auditory.application.internal.commandservices.UsageLogCommandServiceImpl import (
    UsageLogCommandServiceImpl,
)
from src.app.auditory.application.internal.queryservices.UsageLogQueryServiceImpl import (
    UsageLogQueryServiceImpl,
)
from src.app.auditory.application.acl.AuditoryContextFacadeImpl import (
    AuditoryContextFacadeImpl,
)
from src.app.auditory.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemyUsageLogRepository,
)
from src.app.shared.infrastructure.persistence.sqlalchemy import get_session
from src.app.shared.config import settings


async def get_database() -> AsyncIterator[AsyncSession]:
    async for session in get_session():
        yield session


async def get_usage_log_repository(
    database: Annotated[AsyncSession, Depends(get_database)],
) -> SqlAlchemyUsageLogRepository:
    return SqlAlchemyUsageLogRepository(session=database)


async def get_usage_log_command_service(
    repository: Annotated[
        SqlAlchemyUsageLogRepository,
        Depends(get_usage_log_repository),
    ],
) -> UsageLogCommandServiceImpl:
    return UsageLogCommandServiceImpl(usage_log_repository=repository)


async def get_usage_log_query_service(
    repository: Annotated[
        SqlAlchemyUsageLogRepository,
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
