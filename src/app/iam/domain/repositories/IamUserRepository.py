from __future__ import annotations

from typing import Protocol

from src.app.iam.domain.model.entities import IamUser
from src.app.iam.domain.model.valueobjects import UserId


class IamUserRepository(Protocol):
    async def find_by_username(self, username: str) -> IamUser | None:
        ...

    async def find_by_id(self, user_id: UserId) -> IamUser | None:
        ...

    async def save(self, user: IamUser) -> IamUser:
        ...
