from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.app.iam.domain.model.valueobjects import UserRole


class IamUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, description="New account username", examples=["user1"])
    password: str = Field(min_length=1, description="New account password", examples=["secret123"])
    role: UserRole = Field(description="User role", examples=["user", "admin"])
