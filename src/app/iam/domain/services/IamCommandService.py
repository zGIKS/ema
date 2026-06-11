from __future__ import annotations

from typing import Protocol

from src.app.iam.domain.model.commands import AuthenticateUserCommand, CreateUserCommand, UpdateUserRoleCommand
from src.app.iam.domain.model.entities import IamUser


class IamCommandService(Protocol):
    async def handle_authenticate_user(self, command: AuthenticateUserCommand) -> str:
        ...

    async def handle_create_user(self, command: CreateUserCommand) -> IamUser:
        ...

    async def handle_update_user_role(self, command: UpdateUserRoleCommand) -> IamUser:
        ...
