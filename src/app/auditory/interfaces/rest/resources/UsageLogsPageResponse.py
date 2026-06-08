from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.app.auditory.interfaces.rest.resources.UsageLogResource import UsageLogResource


class UsageLogsPageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[UsageLogResource] = Field(description="The list of usage logs in the current page")
    page: int = Field(description="The current page number", examples=[1])
    page_size: int = Field(description="The page size", examples=[20])
    total: int = Field(description="The total number of usage logs", examples=[45])
