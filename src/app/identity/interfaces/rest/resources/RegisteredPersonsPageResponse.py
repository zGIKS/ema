from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.app.identity.interfaces.rest.resources.RegisteredPersonResource import (
    RegisteredPersonResource,
)


class RegisteredPersonsPageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[RegisteredPersonResource] = Field(
        description="Paginated registered persons",
    )
    page: int = Field(gt=0, description="Current page number", examples=[1])
    page_size: int = Field(
        gt=0,
        le=100,
        description="Number of items returned per page",
        examples=[20],
    )
    total: int = Field(ge=0, description="Total registered persons", examples=[42])
