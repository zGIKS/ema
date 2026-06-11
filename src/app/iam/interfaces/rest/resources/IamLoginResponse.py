from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from src.app.shared.validation import UUID_REGEX


class IamLoginResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str = Field(description="Bearer access token")
    user_id: str = Field(pattern=UUID_REGEX, description="Authenticated user id")
    username: str = Field(description="Authenticated username")
