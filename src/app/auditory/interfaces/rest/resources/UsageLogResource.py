from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UsageLogResource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation: str = Field(
        description="The type of operation (e.g., identify, register)",
        examples=["identify"],
    )
    user_id: str | None = Field(
        default=None,
        description="User ID who performed the operation",
        examples=["user-123"],
    )
    person_id: str | None = Field(
        default=None,
        description="Matched or registered person UUID",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    first_name: str | None = Field(
        default=None,
        description="First name of the person",
        examples=["John"],
    )
    last_name: str | None = Field(
        default=None,
        description="Last name of the person",
        examples=["Doe"],
    )
    dni: str | None = Field(
        default=None,
        description="DNI of the person",
        examples=["12345678"],
    )
    confidence: float | None = Field(
        default=None,
        description="Confidence score of the identification",
        examples=[0.91],
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
