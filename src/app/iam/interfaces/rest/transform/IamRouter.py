from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.app.iam.application.internal.commandservices.IamCommandServiceImpl import (
    IamCommandServiceImpl,
)
from src.app.iam.application.internal.queryservices.UserQueryServiceImpl import (
    UserQueryServiceImpl,
)
from src.app.iam.domain.model.commands import AuthenticateUserCommand, CreateUserCommand, UpdateUserRoleCommand
from src.app.iam.domain.model.queries import GetAllUsersQuery
from src.app.iam.domain.model.entities import CurrentUser
from src.app.iam.domain.model.valueobjects import UserId
from src.app.iam.infrastructure.persistence.sqlalchemy.repositories import SqlAlchemyIamUserRepository
from src.app.iam.interfaces.rest.dependencies import require_admin_user
from src.app.iam.interfaces.rest.resources import (
    AuthenticatedUserResource,
    IamLoginRequest,
    IamLoginResponse,
    IamUserRequest,
    UpdateUserRoleRequest,
)
from src.app.identity.interfaces.rest.dependencies import get_database
from src.app.shared.exceptions import AuthenticationError

router = APIRouter(prefix="/api/v1/iam", tags=["IAM"])


@router.post(
    "/login",
    response_model=IamLoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login with username and password",
)
async def login(
    request: IamLoginRequest,
    database=Depends(get_database),
) -> IamLoginResponse:
    repository = SqlAlchemyIamUserRepository(database)
    service = IamCommandServiceImpl(user_repository=repository)
    command = AuthenticateUserCommand(username=request.username, password=request.password)
    token = await service.handle_authenticate_user(command)
    user = await repository.find_by_username(command.username)
    if user is None:
        raise AuthenticationError("Invalid credentials")
    return IamLoginResponse(
        access_token=token,
        user_id=user.user_id.value,
        username=user.username,
    )


@router.post(
    "/users",
    response_model=AuthenticatedUserResource,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
)
async def create_user(
    request: IamUserRequest,
    _current_user: Annotated[CurrentUser, Depends(require_admin_user)],
    database=Depends(get_database),
) -> AuthenticatedUserResource:
    repository = SqlAlchemyIamUserRepository(database)
    service = IamCommandServiceImpl(user_repository=repository)
    user = await service.handle_create_user(
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
    database=Depends(get_database),
) -> AuthenticatedUserResource:
    repository = SqlAlchemyIamUserRepository(database)
    service = IamCommandServiceImpl(user_repository=repository)
    user = await service.handle_update_user_role(
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
    database=Depends(get_database),
) -> list[AuthenticatedUserResource]:
    repository = SqlAlchemyIamUserRepository(database)
    query_service = UserQueryServiceImpl(user_repository=repository)
    users = await query_service.handle_get_all_users(GetAllUsersQuery())
    return [
        AuthenticatedUserResource(
            user_id=u.user_id.value,
            username=u.username,
            role=u.role.value,
        )
        for u in users
    ]
