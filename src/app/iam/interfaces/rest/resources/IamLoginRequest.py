from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class IamLoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(pattern=r"^[A-Za-z]{3,30}$", description="Account username", examples=["mateo"])
    password: str = Field(min_length=1, description="Account password", examples=["secret123"])
