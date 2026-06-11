from __future__ import annotations

from functools import lru_cache
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.app.identity.infrastructure.persistence.sqlalchemy import models as _identity_models  # noqa: F401
from src.app.iam.infrastructure.persistence.sqlalchemy import models as _iam_models  # noqa: F401
from src.app.auditory.infrastructure.persistence.sqlalchemy import models as _auditory_models  # noqa: F401
from src.app.shared.config import settings


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    return create_async_engine(settings.db_url, echo=False)


@lru_cache(maxsize=1)
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with get_session_factory()() as session:
        yield session
