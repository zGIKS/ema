from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.iam.domain.model.entities import IamRefreshToken
from src.app.iam.domain.model.valueobjects import UserId
from src.app.iam.domain.repositories import IamRefreshTokenRepository
from src.app.iam.infrastructure.persistence.sqlalchemy.models import IamRefreshTokenModel


class SqlAlchemyIamRefreshTokenRepository(IamRefreshTokenRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_domain(model: IamRefreshTokenModel) -> IamRefreshToken:
        return IamRefreshToken(
            token_id=model.token_id,
            user_id=UserId(model.user_id),
            token_hash=model.token_hash,
            expires_at=model.expires_at,
            created_at=model.created_at,
            revoked_at=model.revoked_at,
            replaced_by_token_id=model.replaced_by_token_id,
        )

    async def find_by_token_id(self, token_id: str) -> IamRefreshToken | None:
        result = await self._session.execute(
            select(IamRefreshTokenModel).where(IamRefreshTokenModel.token_id == token_id)
        )
        model = result.scalar_one_or_none()
        return None if model is None else self._to_domain(model)

    async def save(self, refresh_token: IamRefreshToken) -> IamRefreshToken:
        result = await self._session.execute(
            select(IamRefreshTokenModel).where(IamRefreshTokenModel.token_id == refresh_token.token_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            model = IamRefreshTokenModel(
                token_id=refresh_token.token_id,
                user_id=refresh_token.user_id.value,
                token_hash=refresh_token.token_hash,
                expires_at=refresh_token.expires_at,
                revoked_at=refresh_token.revoked_at,
                replaced_by_token_id=refresh_token.replaced_by_token_id,
            )
            self._session.add(model)
        else:
            model.user_id = refresh_token.user_id.value
            model.token_hash = refresh_token.token_hash
            model.expires_at = refresh_token.expires_at
            model.revoked_at = refresh_token.revoked_at
            model.replaced_by_token_id = refresh_token.replaced_by_token_id

        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def revoke(self, token_id: str) -> None:
        result = await self._session.execute(
            select(IamRefreshTokenModel).where(IamRefreshTokenModel.token_id == token_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return

        model.revoked_at = datetime.now(UTC)
        await self._session.commit()
