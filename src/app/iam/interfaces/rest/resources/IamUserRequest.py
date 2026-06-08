from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.app.iam.domain.model.valueobjects import UserRole


class IamUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(pattern=r"^U\d{9}$", description="New account username", examples=["U123456789"])
    password: str = Field(min_length=12, description="New account password", examples=["Admin12345!"])
    role: UserRole = Field(description="User role", examples=["user", "admin"])
