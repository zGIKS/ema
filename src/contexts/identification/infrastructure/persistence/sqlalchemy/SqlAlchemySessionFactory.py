from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.contexts.identification.infrastructure.persistence.sqlalchemy import models  # noqa: F401
from src.contexts.identification.infrastructure.persistence.sqlalchemy.models.BaseModel import (
    BaseModel,
)


class SqlAlchemySessionFactory:
    def __init__(self, db_path: str) -> None:
        sqlite_url = f"sqlite+aiosqlite:///{db_path}"
        self._engine: AsyncEngine = create_async_engine(sqlite_url, future=True)
        self._maker = async_sessionmaker(self._engine, expire_on_commit=False)

    async def init_models(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)

    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self._maker() as db_session:
            yield db_session
