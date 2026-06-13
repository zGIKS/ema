from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from src.app.iam.domain.model.commands import (
    AuthenticateUserCommand,
    CreateUserCommand,
    LogoutSessionCommand,
    RefreshSessionCommand,
    UpdateUserRoleCommand,
)
from src.app.iam.domain.model.queries import GetAllUsersQuery
from src.app.iam.domain.model.queries import ResolveBearerTokenQuery
from src.app.iam.domain.model.entities import CurrentUser
from src.app.iam.domain.model.valueobjects import UserId
from src.app.iam.interfaces.rest.dependencies import (
    get_iam_command_service,
    get_current_user,
    get_iam_user_repository,
    get_user_authentication_query_service,
    get_user_query_service,
    require_admin_user,
)
from src.app.iam.interfaces.rest.resources import (
    AuthenticatedUserResource,
    IamLoginRequest,
    IamLoginResponse,
    IamUserRequest,
    UpdateUserRoleRequest,
)
from src.app.shared.config import settings
from src.app.shared.exceptions import AuthenticationError
from src.app.shared.interfaces.rest.resources.ErrorResponse import ErrorResponse

router = APIRouter(prefix="/api/v1/iam", tags=["IAM"])


def _set_refresh_token_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.refresh_token_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.refresh_token_cookie_secure,
        samesite=settings.refresh_token_cookie_samesite,
        max_age=settings.refresh_token_ttl_days * 24 * 60 * 60,
        path=settings.refresh_token_cookie_path,
    )


def _clear_refresh_token_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.refresh_token_cookie_name,
        path=settings.refresh_token_cookie_path,
    )


@router.post(
    "/login",
    response_model=IamLoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login with username and password",
    description="Authenticates the user, returns an access token, and stores a refresh token in an HttpOnly cookie.",
    responses={
        200: {"description": "Login successful"},
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    },
)
async def login(
    request: IamLoginRequest,
    response: Response,
    command_service=Depends(get_iam_command_service),
    user_repository=Depends(get_iam_user_repository),
) -> IamLoginResponse:
    command = AuthenticateUserCommand(username=request.username, password=request.password)
    access_token, refresh_token = await command_service.handle_authenticate_user(command)
    user = await user_repository.find_by_username(command.username)
    if user is None:
        raise AuthenticationError("Invalid credentials")
    _set_refresh_token_cookie(response, refresh_token)
    return IamLoginResponse(
        access_token=access_token,
        user_id=user.user_id.value,
        username=user.username,
    )


@router.post(
    "/refresh",
    response_model=IamLoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh the current session",
    description="Uses the refresh token cookie to issue a new access token and refresh token.",
    responses={
        200: {"description": "Session refreshed"},
        401: {"model": ErrorResponse, "description": "Missing or invalid refresh token"},
    },
)
async def refresh_session(
    request: Request,
    response: Response,
    command_service=Depends(get_iam_command_service),
    auth_service=Depends(get_user_authentication_query_service),
) -> IamLoginResponse:
    refresh_token = request.cookies.get(settings.refresh_token_cookie_name)
    if not refresh_token:
        raise AuthenticationError("Refresh token is required")

    access_token, new_refresh_token = await command_service.handle_refresh_session(
        RefreshSessionCommand(refresh_token=refresh_token)
    )

    current_user = await auth_service.handle_resolve_bearer_token(
        ResolveBearerTokenQuery(token=access_token)
    )
    _set_refresh_token_cookie(response, new_refresh_token)
    return IamLoginResponse(
        access_token=access_token,
        user_id=current_user.user_id.value,
        username=current_user.username,
    )


@router.get(
    "/verify",
    response_model=AuthenticatedUserResource,
    status_code=status.HTTP_200_OK,
    summary="Verify the current access token",
    description="Returns the authenticated user when the bearer access token is valid.",
    responses={
        200: {"description": "Token is valid"},
        401: {"model": ErrorResponse, "description": "Missing or invalid access token"},
    },
)
async def verify_token(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> AuthenticatedUserResource:
    return AuthenticatedUserResource(
        user_id=current_user.user_id.value,
        username=current_user.username,
        role=current_user.role.value,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout current session",
    description="Revokes the refresh token cookie and clears the session cookie on the client.",
    responses={
        204: {"description": "Logged out"},
    },
)
async def logout_session(
    request: Request,
    response: Response,
    command_service=Depends(get_iam_command_service),
) -> Response:
    refresh_token = request.cookies.get(settings.refresh_token_cookie_name)
    if refresh_token:
        await command_service.handle_logout_session(LogoutSessionCommand(refresh_token=refresh_token))

    _clear_refresh_token_cookie(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.post(
    "/users",
    response_model=AuthenticatedUserResource,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
)
async def create_user(
    request: IamUserRequest,
    _current_user: Annotated[CurrentUser, Depends(require_admin_user)],
    command_service=Depends(get_iam_command_service),
) -> AuthenticatedUserResource:
    user = await command_service.handle_create_user(
        CreateUserCommand(
            username=request.username,
            password=request.password,
        )
    )
    return AuthenticatedUserResource(user_id=user.user_id.value, username=user.username, role=user.role.value)


@router.patch(
    "/users/{user_id}/role",
    response_model=AuthenticatedUserResource,
    status_code=status.HTTP_200_OK,
    summary="Update a user role",
)
async def update_user_role(
    user_id: str,
    request: UpdateUserRoleRequest,
    _current_user: Annotated[CurrentUser, Depends(require_admin_user)],
    command_service=Depends(get_iam_command_service),
) -> AuthenticatedUserResource:
    user = await command_service.handle_update_user_role(
        UpdateUserRoleCommand(
            user_id=UserId(user_id),
            role=request.role,
        )
    )
    return AuthenticatedUserResource(user_id=user.user_id.value, username=user.username, role=user.role.value)


@router.get(
    "/users",
    response_model=list[AuthenticatedUserResource],
    status_code=status.HTTP_200_OK,
    summary="Get all users with their roles (Admin only)",
)
async def get_all_users(
    _current_user: Annotated[CurrentUser, Depends(require_admin_user)],
    query_service=Depends(get_user_query_service),
) -> list[AuthenticatedUserResource]:
    users = await query_service.handle_get_all_users(GetAllUsersQuery())
    return [
        AuthenticatedUserResource(
            user_id=u.user_id.value,
            username=u.username,
            role=u.role.value,
        )
        for u in users
    ]
