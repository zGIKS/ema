from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.auditory.domain.model.entities.UsageLog import UsageLog
from src.app.auditory.domain.repositories.UsageLogRepository import UsageLogRepository
from src.app.auditory.infrastructure.persistence.sqlalchemy.models import UsageLogModel


class SqlAlchemyUsageLogRepository(UsageLogRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_domain(model: UsageLogModel) -> UsageLog:
        return UsageLog(
            user_id=model.user_id,
            operation=model.operation,
            person_id=model.person_id,
            first_name=model.first_name,
            last_name=model.last_name,
            dni=model.dni,
            confidence=model.confidence,
            samples_added=model.samples_added,
            total_samples=model.total_samples,
            duration_ms=model.duration_ms,
            image_url=model.image_url,
            used_at=model.used_at,
        )

    async def log_identify(
        self,
        *,
        user_id: str,
        person_id: str | None,
        first_name: str | None = None,
        last_name: str | None = None,
        dni: str | None = None,
        confidence: float | None,
        duration_ms: int,
        image_url: str | None = None,
    ) -> None:
        self._session.add(
            UsageLogModel(
                # Let the ORM assign the UUID and timestamp defaults.
                user_id=user_id,
                operation="identify",
                person_id=person_id,
                first_name=first_name,
                last_name=last_name,
                dni=dni,
                confidence=float(confidence) if confidence is not None else None,
                duration_ms=int(duration_ms),
                image_url=image_url,
            )
        )
        await self._session.commit()

    async def log_register(
        self,
        *,
        user_id: str,
        person_id: str,
        first_name: str,
        last_name: str,
        dni: str,
        duration_ms: int,
        image_url: str | None = None,
    ) -> None:
        self._session.add(
            UsageLogModel(
                user_id=user_id,
                operation="register",
                person_id=person_id,
                first_name=first_name,
                last_name=last_name,
                dni=dni,
                confidence=None,
                duration_ms=int(duration_ms),
                image_url=image_url,
            )
        )
        await self._session.commit()

    async def log_add_person_face_samples(
        self,
        *,
        user_id: str,
        person_id: str,
        first_name: str,
        last_name: str,
        dni: str,
        samples_added: int,
        total_samples: int,
        duration_ms: int,
    ) -> None:
        self._session.add(
            UsageLogModel(
                user_id=user_id,
                operation="add_face_samples",
                person_id=person_id,
                first_name=first_name,
                last_name=last_name,
                dni=dni,
                confidence=None,
                samples_added=int(samples_added),
                total_samples=int(total_samples),
                duration_ms=int(duration_ms),
            )
        )
        await self._session.commit()

    async def find_paginated(
        self,
        *,
        page: int,
        page_size: int,
        user_id: str | None = None,
    ) -> tuple[tuple[UsageLog, ...], int]:
        offset = (page - 1) * page_size
        stmt = select(UsageLogModel)
        if user_id is not None:
            stmt = stmt.where(UsageLogModel.user_id == user_id)

        total_stmt = select(func.count()).select_from(UsageLogModel)
        if user_id is not None:
            total_stmt = total_stmt.where(UsageLogModel.user_id == user_id)

        total = int((await self._session.execute(total_stmt)).scalar_one())
        result = await self._session.execute(stmt.order_by(UsageLogModel.used_at.desc()).offset(offset).limit(page_size))
        docs = result.scalars().all()

        return (
            tuple(self._to_domain(doc) for doc in docs),
            total,
        )
