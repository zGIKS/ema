from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class IamLoginResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str = Field(description="Bearer access token")
    user_id: str = Field(description="Authenticated user id")
    username: str = Field(description="Authenticated username")
