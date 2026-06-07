from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class BoundingBoxResource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: int = Field(ge=0, description="Bounding box X coordinate", examples=[100])
    y: int = Field(ge=0, description="Bounding box Y coordinate", examples=[80])
    w: int = Field(gt=0, description="Bounding box width", examples=[120])
    h: int = Field(gt=0, description="Bounding box height", examples=[120])
