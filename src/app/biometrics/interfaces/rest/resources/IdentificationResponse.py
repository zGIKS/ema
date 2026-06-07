from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class IdentificationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    uuid: str | None = Field(
        default=None,
        description="Matched person UUID when the confidence reaches the threshold",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    first_name: str | None = Field(
        default=None,
        description="Matched person's first name",
        examples=["Jose Luis"],
    )
    last_name: str | None = Field(
        default=None,
        description="Matched person's last name",
        examples=["Quispe Nunez"],
    )
    dni: str | None = Field(
        default=None,
        description="Matched person's Peruvian DNI",
        examples=["12345678"],
    )
    photo: str | None = Field(
        default=None,
        description="Base64-encoded representative photo of the matched person",
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score normalized to the [0,1] range",
        examples=[0.91],
    )
