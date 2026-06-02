from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RegisterResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    person_id: str = Field(
        min_length=1,
        description="Identifier assigned to the enrolled person",
        examples=["person_001"],
    )
    enrolled: bool = Field(
        description="True when all submitted face samples were enrolled",
        examples=[True],
    )
