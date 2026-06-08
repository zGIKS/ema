from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.app.iam.application.internal.queryservices.JwtUserAuthenticationQueryServiceImpl import (
    JwtUserAuthenticationQueryServiceImpl,
)
from src.app.iam.domain.model.entities import CurrentUser
from src.app.iam.domain.model.queries import ResolveBearerTokenQuery
from src.app.iam.domain.model.valueobjects import UserRole
from src.app.shared.exceptions import AuthenticationError, AuthorizationError

_bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache(maxsize=1)
def get_user_authentication_query_service() -> JwtUserAuthenticationQueryServiceImpl:
    return JwtUserAuthenticationQueryServiceImpl()


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_bearer_scheme),
    ],
    auth_service: Annotated[
        JwtUserAuthenticationQueryServiceImpl,
        Depends(get_user_authentication_query_service),
    ],
) -> CurrentUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationError("Bearer token is required")

    return await auth_service.handle_resolve_bearer_token(
        ResolveBearerTokenQuery(token=credentials.credentials)
    )


async def require_admin_user(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    if current_user.role is not UserRole.ADMIN:
        raise AuthorizationError("Admin role required")

    return current_user
