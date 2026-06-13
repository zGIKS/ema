from __future__ import annotations

from typing import Protocol

from src.app.iam.domain.model.commands import (
    AuthenticateUserCommand,
    CreateUserCommand,
    LogoutSessionCommand,
    RefreshSessionCommand,
    UpdateUserRoleCommand,
)
from src.app.iam.domain.model.entities import IamUser


class IamCommandService(Protocol):
    async def handle_authenticate_user(self, command: AuthenticateUserCommand) -> tuple[str, str]:
        ...

    async def handle_refresh_session(self, command: RefreshSessionCommand) -> tuple[str, str]:
        ...

    async def handle_logout_session(self, command: LogoutSessionCommand) -> None:
        ...

    async def handle_create_user(self, command: CreateUserCommand) -> IamUser:
        ...

    async def handle_update_user_role(self, command: UpdateUserRoleCommand) -> IamUser:
        ...
