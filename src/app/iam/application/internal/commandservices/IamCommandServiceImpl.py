from __future__ import annotations

from datetime import UTC, datetime, timedelta
from secrets import randbelow

import jwt

from src.app.iam.domain.model.commands import AuthenticateUserCommand, CreateUserCommand
from src.app.iam.domain.model.entities import IamUser
from src.app.iam.domain.model.valueobjects import UserId
from src.app.iam.domain.repositories import IamUserRepository
from src.app.iam.domain.services import IamCommandService
from src.app.shared.config import settings
from src.app.shared.exceptions import AuthenticationError, ConflictError


def _hash_password(password: str) -> str:
    import base64
    import hashlib
    import os

    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return "pbkdf2_sha256$120000$%s$%s" % (
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(digest).decode("ascii"),
    )


def _verify_password(password: str, hashed: str) -> bool:
    import base64
    import hashlib
    import hmac

    try:
        scheme, iterations, salt_b64, digest_b64 = hashed.split("$")
    except ValueError as error:
        raise AuthenticationError("Invalid password hash format") from error

    if scheme != "pbkdf2_sha256":
        raise AuthenticationError("Unsupported password hash")

    salt = base64.b64decode(salt_b64)
    expected = base64.b64decode(digest_b64)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
    return hmac.compare_digest(derived, expected)


class IamCommandServiceImpl(IamCommandService):
    _jwt_algorithm = "HS256"

    def __init__(self, *, user_repository: IamUserRepository) -> None:
        self._user_repository = user_repository

    async def handle_authenticate_user(self, command: AuthenticateUserCommand) -> str:
        user = await self._user_repository.find_by_username(command.username)
        if user is None or not user.is_active:
            raise AuthenticationError("Invalid credentials")

        if not _verify_password(command.password, user.password_hash):
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
            password_hash=_hash_password(command.password),
            role=command.role,
            is_active=True,
        )
        return await self._user_repository.save(user)

    async def _generate_unique_user_id(self) -> str:
        for _ in range(100):
            candidate = f"U{randbelow(1_000_000_000):09d}"
            if await self._user_repository.find_by_id(UserId(candidate)) is None:
                return candidate

        raise ConflictError("Unable to generate a unique user_id")
