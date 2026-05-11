from __future__ import annotations

from pydantic import BaseModel, Field


class BoundingBoxDTO(BaseModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    w: int = Field(gt=0)
    h: int = Field(gt=0)


class IdentificationResponse(BaseModel):
    person_id: str | None
    confidence: float = Field(ge=0.0, le=1.0)
    box: BoundingBoxDTO | None = None


class RegisterResponse(BaseModel):
    person_id: str
    enrolled: bool

