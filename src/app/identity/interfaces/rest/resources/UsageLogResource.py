from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UsageLogResource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation: str = Field(
        description="The type of operation (e.g., identify, register)",
        examples=["identify"],
    )
    person_id: str | None = Field(
        default=None,
        description="Matched or registered person UUID",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    confidence: float | None = Field(
        default=None,
        description="Confidence score of the identification",
        examples=[0.91],
    )
    samples_added: int | None = Field(
        default=None,
        description="Number of face samples added in the operation",
        examples=[2],
    )
    total_samples: int | None = Field(
        default=None,
        description="Total enrolled samples after the operation",
        examples=[5],
    )
    duration_ms: int = Field(
        description="Duration of the operation in milliseconds",
        examples=[120],
    )
    image_url: str | None = Field(
        default=None,
        description="Cloudinary URL of the query/representative photo",
        examples=["https://res.cloudinary.com/demo/image/upload/v1719307544/sample.jpg"],
    )
    used_at: int = Field(
        description="Timestamp when the operation was performed",
        examples=[1719307544],
    )
