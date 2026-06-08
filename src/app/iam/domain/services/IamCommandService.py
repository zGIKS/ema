from __future__ import annotations

from typing import Protocol

from src.app.iam.domain.model.commands import AuthenticateUserCommand, CreateUserCommand
from src.app.iam.domain.model.entities import IamUser


class IamCommandService(Protocol):
    async def handle_authenticate_user(self, command: AuthenticateUserCommand) -> str:
        ...

    async def handle_create_user(self, command: CreateUserCommand) -> IamUser:
        ...
