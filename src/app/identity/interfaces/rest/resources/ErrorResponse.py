from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    detail: str = Field(
        min_length=1,
        description="Human-readable description of the error",
        examples=["image_bytes cannot be empty"],
    )
