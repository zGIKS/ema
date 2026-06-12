from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.iam.domain.model.entities import IamUser
from src.app.iam.domain.model.valueobjects import UserId, UserRole
from src.app.iam.domain.repositories import IamUserRepository
from src.app.iam.infrastructure.persistence.sqlalchemy.models import IamUserModel


class SqlAlchemyIamUserRepository(IamUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_domain(model: IamUserModel) -> IamUser:
        return IamUser(
            user_id=UserId(model.user_id),
            username=model.username,
            password_hash=model.password_hash,
            role=UserRole.from_value(model.role),
            is_active=bool(model.is_active),
        )

    async def find_by_username(self, username: str) -> IamUser | None:
        result = await self._session.execute(select(IamUserModel).where(IamUserModel.username == username))
        model = result.scalar_one_or_none()
        return None if model is None else self._to_domain(model)

    async def find_by_id(self, user_id: UserId) -> IamUser | None:
        result = await self._session.execute(select(IamUserModel).where(IamUserModel.user_id == user_id.value))
        model = result.scalar_one_or_none()
        return None if model is None else self._to_domain(model)

    async def save(self, user: IamUser) -> IamUser:
        result = await self._session.execute(select(IamUserModel).where(IamUserModel.user_id == user.user_id.value))
        model = result.scalar_one_or_none()
        if model is None:
            model = IamUserModel(
                user_id=user.user_id.value,
                username=user.username,
                password_hash=user.password_hash,
                role=user.role.value,
                is_active=user.is_active,
            )
            self._session.add(model)
        else:
            model.username = user.username
            model.password_hash = user.password_hash
            model.role = user.role.value
            model.is_active = user.is_active

        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def find_all(self) -> list[IamUser]:
        result = await self._session.execute(select(IamUserModel))
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]
