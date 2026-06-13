from __future__ import annotations

import jwt

from src.app.iam.domain.model.entities import CurrentUser
from src.app.iam.domain.model.queries import ResolveBearerTokenQuery
from src.app.iam.domain.model.valueobjects import UserId, UserRole
from src.app.iam.domain.services import UserAuthenticationQueryService
from src.app.shared.config import settings
from src.app.shared.exceptions import AuthenticationError


class JwtUserAuthenticationQueryServiceImpl(UserAuthenticationQueryService):
    _jwt_algorithm = "HS256"

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
        username = payload.get("username")
        role = payload.get("role")

        if token_type != "access":
            raise AuthenticationError("Invalid bearer token")
        if not isinstance(user_id, str) or not user_id.strip():
            raise AuthenticationError("Token is missing subject")
        if not isinstance(username, str) or not username.strip():
            raise AuthenticationError("Token is missing username")
        if not isinstance(role, str) or not role.strip():
            raise AuthenticationError("Token is missing role")

        return CurrentUser(
            user_id=UserId(user_id),
            username=username,
            role=UserRole.from_value(role),
        )
