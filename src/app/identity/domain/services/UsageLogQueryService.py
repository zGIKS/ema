from __future__ import annotations

from typing import Protocol

from src.app.identity.domain.model.queries.GetUsageLogsQuery import GetUsageLogsQuery
from src.app.identity.domain.model.results.UsageLogsPageResult import UsageLogsPageResult


class UsageLogQueryService(Protocol):
    async def handle_get_usage_logs(self, query: GetUsageLogsQuery) -> UsageLogsPageResult:
        ...
