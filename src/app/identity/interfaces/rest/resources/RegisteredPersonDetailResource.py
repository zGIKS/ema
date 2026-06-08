from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RegisteredPersonDetailResource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    uuid: str = Field(
        description="Unique identifier of the registered person",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    first_name: str = Field(
        description="Registered person's first name",
        examples=["Jose Luis"],
    )
    last_name: str = Field(
        description="Registered person's last name",
        examples=["Quispe Nunez"],
    )
    dni: str = Field(
        description="Peruvian DNI with exactly 8 digits",
        examples=["12345678"],
    )
    image_url: str | None = Field(
        default=None,
        description="Cloudinary URL of the representative photo",
        examples=["https://res.cloudinary.com/demo/image/upload/v1719307544/sample.jpg"],
    )
    sample_image_urls: list[str | None] = Field(
        default_factory=list,
        description="Cloudinary URLs of all enrolled face samples for this person",
        examples=[["https://res.cloudinary.com/demo/image/upload/v1719307544/sample.jpg"]],
    )
    total_samples: int = Field(
        ge=0,
        description="Total number of enrolled face samples",
        examples=[3],
    )
