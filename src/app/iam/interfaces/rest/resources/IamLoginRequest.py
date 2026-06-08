from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class IamLoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, description="Account username", examples=["admin"])
    password: str = Field(min_length=1, description="Account password", examples=["secret123"])
