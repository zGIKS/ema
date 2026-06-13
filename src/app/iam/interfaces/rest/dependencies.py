from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.app.iam.application.internal.commandservices.IamCommandServiceImpl import (
    IamCommandServiceImpl,
)
from src.app.iam.application.internal.queryservices.JwtUserAuthenticationQueryServiceImpl import (
    JwtUserAuthenticationQueryServiceImpl,
)
from src.app.iam.application.internal.queryservices.UserQueryServiceImpl import (
    UserQueryServiceImpl,
)
from src.app.iam.domain.model.entities import CurrentUser
from src.app.iam.domain.model.queries import ResolveBearerTokenQuery
from src.app.iam.domain.model.valueobjects import UserRole
from src.app.iam.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemyIamRefreshTokenRepository,
    SqlAlchemyIamUserRepository,
)
from src.app.shared.infrastructure.persistence.sqlalchemy import get_session
from src.app.shared.exceptions import AuthenticationError, AuthorizationError

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_database() -> AsyncIterator[AsyncSession]:
    async for session in get_session():
        yield session


async def get_iam_user_repository(
    database: Annotated[AsyncSession, Depends(get_database)],
) -> SqlAlchemyIamUserRepository:
    return SqlAlchemyIamUserRepository(database)


async def get_iam_refresh_token_repository(
    database: Annotated[AsyncSession, Depends(get_database)],
) -> SqlAlchemyIamRefreshTokenRepository:
    return SqlAlchemyIamRefreshTokenRepository(database)


async def get_iam_command_service(
    user_repository: Annotated[
        SqlAlchemyIamUserRepository,
        Depends(get_iam_user_repository),
    ],
    refresh_token_repository: Annotated[
        SqlAlchemyIamRefreshTokenRepository,
        Depends(get_iam_refresh_token_repository),
    ],
) -> IamCommandServiceImpl:
    return IamCommandServiceImpl(
        user_repository=user_repository,
        refresh_token_repository=refresh_token_repository,
    )


async def get_user_query_service(
    user_repository: Annotated[
        SqlAlchemyIamUserRepository,
        Depends(get_iam_user_repository),
    ],
) -> UserQueryServiceImpl:
    return UserQueryServiceImpl(user_repository=user_repository)


async def get_user_authentication_query_service(
    user_repository: Annotated[
        SqlAlchemyIamUserRepository,
        Depends(get_iam_user_repository),
    ],
) -> JwtUserAuthenticationQueryServiceImpl:
    return JwtUserAuthenticationQueryServiceImpl(user_repository=user_repository)


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
