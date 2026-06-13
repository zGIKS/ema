from __future__ import annotations

from typing import Protocol

from src.app.iam.domain.model.entities import IamRefreshToken


class IamRefreshTokenRepository(Protocol):
    async def find_by_token_id(self, token_id: str) -> IamRefreshToken | None:
        ...

    async def save(self, refresh_token: IamRefreshToken) -> IamRefreshToken:
        ...

    async def revoke(self, token_id: str) -> None:
        ...
