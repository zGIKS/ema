from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, status

from src.app.auditory.application.internal.queryservices.UsageLogQueryServiceImpl import (
    UsageLogQueryServiceImpl,
)
from src.app.auditory.domain.model.queries.GetUsageLogsQuery import GetUsageLogsQuery
from src.app.auditory.interfaces.rest.resources.UsageLogResource import UsageLogResource
from src.app.auditory.interfaces.rest.resources.UsageLogsPageResponse import (
    UsageLogsPageResponse,
)
from src.app.auditory.interfaces.rest.dependencies import get_usage_log_query_service


router = APIRouter(prefix="/api/v1/auditory", tags=["Auditory"])


@router.get(
    "/usage-logs",
    response_model=UsageLogsPageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get usage logs",
    description="Returns a paginated list of usage/identification logs.",
)
async def get_usage_logs(
    query_service: Annotated[
        UsageLogQueryServiceImpl,
        Depends(get_usage_log_query_service),
    ],
    page: int = 1,
    page_size: int = 20,
) -> UsageLogsPageResponse:
    query = GetUsageLogsQuery(page=page, page_size=page_size)
    logs_page = await query_service.handle_get_usage_logs(query)

    return UsageLogsPageResponse(
        items=[
            UsageLogResource(
                operation=log.operation,
                person_id=log.person_id,
                confidence=log.confidence,
                duration_ms=log.duration_ms,
                image_url=log.image_url,
                used_at=log.used_at,
            )
            for log in logs_page.items
        ],
        page=logs_page.page,
        page_size=logs_page.page_size,
        total=logs_page.total,
    )
