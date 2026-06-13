from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class IamUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(pattern=r"^[A-Za-z]{3,30}$", description="New account username", examples=["mateo"])
    password: str = Field(min_length=12, description="New account password", examples=["Admin12345!"])
