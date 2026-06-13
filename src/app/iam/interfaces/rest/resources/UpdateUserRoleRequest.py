from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.app.iam.domain.model.valueobjects import UserRole


class UpdateUserRoleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: UserRole = Field(description="User role", examples=["user", "admin"])
