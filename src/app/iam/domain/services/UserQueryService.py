from __future__ import annotations

from typing import Protocol

from src.app.iam.domain.model.entities import IamUser
from src.app.iam.domain.model.queries import GetAllUsersQuery


class UserQueryService(Protocol):
    async def handle_get_all_users(
        self,
        query: GetAllUsersQuery,
    ) -> list[IamUser]:
        ...
