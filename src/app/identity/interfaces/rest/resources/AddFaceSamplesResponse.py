from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddFaceSamplesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    person_id: str = Field(
        min_length=1,
        description="Person identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    total_samples: int = Field(
        ge=1,
        description="Total enrolled face samples after the upload",
        examples=[3],
    )
