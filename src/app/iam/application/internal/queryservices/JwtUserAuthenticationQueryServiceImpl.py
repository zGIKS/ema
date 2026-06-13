from __future__ import annotations

import jwt

from src.app.iam.domain.model.entities import CurrentUser
from src.app.iam.domain.model.queries import ResolveBearerTokenQuery
from src.app.iam.domain.model.valueobjects import UserId
from src.app.iam.domain.repositories import IamUserRepository
from src.app.iam.domain.services import UserAuthenticationQueryService
from src.app.shared.config import settings
from src.app.shared.exceptions import AuthenticationError


class JwtUserAuthenticationQueryServiceImpl(UserAuthenticationQueryService):
    _jwt_algorithm = "HS256"

    def __init__(self, user_repository: IamUserRepository) -> None:
        self._user_repository = user_repository

    async def handle_resolve_bearer_token(self, query: ResolveBearerTokenQuery) -> CurrentUser:
        try:
            payload = jwt.decode(
                query.token,
                settings.jwt_secret,
                algorithms=[self._jwt_algorithm],
            )
        except jwt.ExpiredSignatureError as error:
            raise AuthenticationError("Token has expired") from error
        except jwt.InvalidTokenError as error:
            raise AuthenticationError("Invalid bearer token") from error

        token_type = payload.get("typ")
        user_id = payload.get("sub")

        if token_type != "access":
            raise AuthenticationError("Invalid bearer token")
        if not isinstance(user_id, str) or not user_id.strip():
            raise AuthenticationError("Token is missing subject")

        user = await self._user_repository.find_by_id(UserId(user_id))
        if user is None or not user.is_active:
            raise AuthenticationError("User is inactive or no longer exists")

        return CurrentUser(
            user_id=user.user_id,
            username=user.username,
            role=user.role,
        )
