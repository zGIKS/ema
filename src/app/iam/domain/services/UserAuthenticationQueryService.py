from __future__ import annotations

from typing import Protocol

from src.app.iam.domain.model.entities import CurrentUser
from src.app.iam.domain.model.queries import ResolveBearerTokenQuery


class UserAuthenticationQueryService(Protocol):
    async def handle_resolve_bearer_token(self, query: ResolveBearerTokenQuery) -> CurrentUser:
        ...
