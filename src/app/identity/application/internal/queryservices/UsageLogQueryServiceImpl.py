from __future__ import annotations

from src.app.identity.domain.model.queries.GetUsageLogsQuery import GetUsageLogsQuery
from src.app.identity.domain.model.results.UsageLogsPageResult import UsageLogsPageResult
from src.app.identity.domain.repositories.UsageLogRepository import UsageLogRepository
from src.app.identity.domain.services.UsageLogQueryService import UsageLogQueryService


class UsageLogQueryServiceImpl(UsageLogQueryService):
    def __init__(self, *, usage_log_repository: UsageLogRepository) -> None:
        self._usage_log_repository = usage_log_repository

    async def handle_get_usage_logs(
        self,
        query: GetUsageLogsQuery,
    ) -> UsageLogsPageResult:
        logs, total = await self._usage_log_repository.find_paginated(
            page=query.page,
            page_size=query.page_size,
        )
        return UsageLogsPageResult(
            items=logs,
            page=query.page,
            page_size=query.page_size,
            total=total,
        )
