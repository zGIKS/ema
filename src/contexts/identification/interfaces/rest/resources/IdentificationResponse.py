from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.contexts.identification.interfaces.rest.resources.BoundingBoxResource import (
    BoundingBoxResource,
)


class IdentificationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    person_id: str | None = Field(
        default=None,
        description="Matched person identifier when confidence reaches the threshold",
        examples=["person_001"],
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score normalized to the [0,1] range",
        examples=[0.91],
    )
    box: BoundingBoxResource | None = Field(
        default=None,
        description="Detected face bounding box",
    )
