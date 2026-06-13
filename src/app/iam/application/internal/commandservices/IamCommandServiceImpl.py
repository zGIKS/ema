from __future__ import annotations

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import uuid4

import jwt

from src.app.iam.domain.model.commands import (
    AuthenticateUserCommand,
    CreateUserCommand,
    LogoutSessionCommand,
    RefreshSessionCommand,
    UpdateUserRoleCommand,
)
from src.app.iam.domain.model.entities import IamRefreshToken
from src.app.iam.domain.model.entities import IamUser
from src.app.iam.domain.model.valueobjects import UserId, UserRole
from src.app.iam.domain.repositories import IamRefreshTokenRepository, IamUserRepository
from src.app.iam.domain.services import IamCommandService
from src.app.shared.config import settings
from src.app.shared.exceptions import AuthenticationError, ConflictError
from src.app.shared.exceptions import NotFoundError
from src.app.iam.infrastructure.security.passwords import encode_password, verify_password


class IamCommandServiceImpl(IamCommandService):
    _jwt_algorithm = "HS256"

    def __init__(
        self,
        *,
        user_repository: IamUserRepository,
        refresh_token_repository: IamRefreshTokenRepository,
    ) -> None:
        self._user_repository = user_repository
        self._refresh_token_repository = refresh_token_repository

    async def handle_authenticate_user(self, command: AuthenticateUserCommand) -> tuple[str, str]:
        user = await self._user_repository.find_by_username(command.username)
        if user is None or not user.is_active:
            raise AuthenticationError("Invalid credentials")

        if not verify_password(command.password, user.password_hash):
            raise AuthenticationError("Invalid credentials")

        now = datetime.now(UTC)
        access_token = self._build_access_token(user, now)
        refresh_token, refresh_record = self._build_refresh_token(user, now)
        await self._refresh_token_repository.save(refresh_record)
        return access_token, refresh_token

    async def handle_refresh_session(self, command: RefreshSessionCommand) -> tuple[str, str]:
        payload = self._decode_refresh_token(command.refresh_token)

        token_id = payload.get("jti")
        user_id = payload.get("sub")
        if not isinstance(token_id, str) or not token_id.strip():
            raise AuthenticationError("Refresh token is missing id")
        if not isinstance(user_id, str) or not user_id.strip():
            raise AuthenticationError("Refresh token is missing subject")

        stored_token = await self._refresh_token_repository.find_by_token_id(token_id)
        if stored_token is None:
            raise AuthenticationError("Invalid refresh token")

        if stored_token.revoked_at is not None:
            raise AuthenticationError("Refresh token has been revoked")

        if stored_token.token_hash != self._hash_token(command.refresh_token):
            raise AuthenticationError("Invalid refresh token")

        user = await self._user_repository.find_by_id(UserId(user_id))
        if user is None or not user.is_active:
            raise AuthenticationError("Invalid refresh token")

        await self._refresh_token_repository.revoke(token_id)

        now = datetime.now(UTC)
        access_token = self._build_access_token(user, now)
        new_refresh_token, new_refresh_record = self._build_refresh_token(user, now)
        await self._refresh_token_repository.save(new_refresh_record)
        return access_token, new_refresh_token

    async def handle_logout_session(self, command: LogoutSessionCommand) -> None:
        try:
            payload = self._decode_refresh_token(command.refresh_token)
        except AuthenticationError:
            return

        token_id = payload.get("jti")
        if not isinstance(token_id, str) or not token_id.strip():
            return

        await self._refresh_token_repository.revoke(token_id)

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

    def _build_access_token(self, user: IamUser, now: datetime) -> str:
        payload = {
            "sub": user.user_id.value,
            "username": user.username,
            "role": user.role.value,
            "typ": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=settings.access_token_ttl_minutes)).timestamp()),
        }
        return jwt.encode(payload, settings.jwt_secret, algorithm=self._jwt_algorithm)

    def _build_refresh_token(self, user: IamUser, now: datetime) -> tuple[str, IamRefreshToken]:
        token_id = str(uuid4())
        payload = {
            "sub": user.user_id.value,
            "jti": token_id,
            "typ": "refresh",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(days=settings.refresh_token_ttl_days)).timestamp()),
        }
        refresh_token = jwt.encode(payload, settings.jwt_secret, algorithm=self._jwt_algorithm)
        refresh_record = IamRefreshToken(
            token_id=token_id,
            user_id=user.user_id,
            token_hash=self._hash_token(refresh_token),
            expires_at=now + timedelta(days=settings.refresh_token_ttl_days),
        )
        return refresh_token, refresh_record

    def _decode_refresh_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[self._jwt_algorithm],
            )
        except jwt.ExpiredSignatureError as error:
            raise AuthenticationError("Refresh token has expired") from error
        except jwt.InvalidTokenError as error:
            raise AuthenticationError("Invalid refresh token") from error

        if payload.get("typ") != "refresh":
            raise AuthenticationError("Invalid refresh token")

        return payload

    @staticmethod
    def _hash_token(token: str) -> str:
        return sha256(token.encode("utf-8")).hexdigest()

    async def _generate_unique_user_id(self) -> str:
        for _ in range(100):
            candidate = str(uuid4())
            if await self._user_repository.find_by_id(UserId(candidate)) is None:
                return candidate

        raise ConflictError("Unable to generate a unique user_id")
