from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt

from src.app.iam.domain.model.commands import AuthenticateUserCommand, CreateUserCommand, UpdateUserRoleCommand
from src.app.iam.domain.model.entities import IamUser
from src.app.iam.domain.model.valueobjects import UserId, UserRole
from src.app.iam.domain.repositories import IamUserRepository
from src.app.iam.domain.services import IamCommandService
from src.app.shared.config import settings
from src.app.shared.exceptions import AuthenticationError, ConflictError
from src.app.shared.exceptions import NotFoundError
from src.app.iam.infrastructure.security.passwords import encode_password, verify_password


class IamCommandServiceImpl(IamCommandService):
    _jwt_algorithm = "HS256"

    def __init__(self, *, user_repository: IamUserRepository) -> None:
        self._user_repository = user_repository

    async def handle_authenticate_user(self, command: AuthenticateUserCommand) -> str:
        user = await self._user_repository.find_by_username(command.username)
        if user is None or not user.is_active:
            raise AuthenticationError("Invalid credentials")

        if not verify_password(command.password, user.password_hash):
            raise AuthenticationError("Invalid credentials")

        now = datetime.now(UTC)
        payload = {
            "sub": user.user_id.value,
            "username": user.username,
            "role": user.role.value,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=12)).timestamp()),
        }
        return jwt.encode(payload, settings.jwt_secret, algorithm=self._jwt_algorithm)

    async def handle_create_user(self, command: CreateUserCommand) -> IamUser:
        existing = await self._user_repository.find_by_username(command.username)
        if existing is not None:
            raise ConflictError("Username already exists")

        user_id = await self._generate_unique_user_id()

        user = IamUser(
            user_id=UserId(user_id),
            username=command.username,
            password_hash=encode_password(command.password),
            role=UserRole.USER,
            is_active=True,
        )
        return await self._user_repository.save(user)

    async def handle_update_user_role(self, command: UpdateUserRoleCommand) -> IamUser:
        existing = await self._user_repository.find_by_id(command.user_id)
        if existing is None:
            raise NotFoundError("User not found")

        updated_user = IamUser(
            user_id=existing.user_id,
            username=existing.username,
            password_hash=existing.password_hash,
            role=command.role,
            is_active=existing.is_active,
        )
        return await self._user_repository.save(updated_user)

    async def _generate_unique_user_id(self) -> str:
        for _ in range(100):
            candidate = str(uuid4())
            if await self._user_repository.find_by_id(UserId(candidate)) is None:
                return candidate

        raise ConflictError("Unable to generate a unique user_id")
