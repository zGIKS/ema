from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AuthenticatedUserResource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(description="Authenticated user id")
    username: str = Field(description="Authenticated username")
    role: str = Field(description="Authenticated role")
