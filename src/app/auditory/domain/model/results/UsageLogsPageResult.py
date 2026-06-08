from __future__ import annotations

from dataclasses import dataclass

from src.app.auditory.domain.model.entities.UsageLog import UsageLog


@dataclass(frozen=True, slots=True)
class UsageLogsPageResult:
    items: tuple[UsageLog, ...]
    page: int
    page_size: int
    total: int
