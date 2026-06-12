from __future__ import annotations

from src.app.iam.domain.model.entities import IamUser
from src.app.iam.domain.model.queries import GetAllUsersQuery
from src.app.iam.domain.repositories import IamUserRepository
from src.app.iam.domain.services import UserQueryService


class UserQueryServiceImpl(UserQueryService):
    def __init__(self, user_repository: IamUserRepository) -> None:
        self._user_repository = user_repository

    async def handle_get_all_users(
        self,
        query: GetAllUsersQuery,
    ) -> list[IamUser]:
        return await self._user_repository.find_all()
