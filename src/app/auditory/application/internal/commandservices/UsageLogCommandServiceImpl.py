from __future__ import annotations

from src.app.auditory.domain.model.commands.LogIdentifyCommand import LogIdentifyCommand
from src.app.auditory.domain.model.commands.LogRegisterCommand import LogRegisterCommand
from src.app.auditory.domain.repositories.UsageLogRepository import UsageLogRepository
from src.app.auditory.domain.services.UsageLogCommandService import UsageLogCommandService


class UsageLogCommandServiceImpl(UsageLogCommandService):
    def __init__(self, *, usage_log_repository: UsageLogRepository) -> None:
        self._usage_log_repository = usage_log_repository

    async def handle_log_identify(self, command: LogIdentifyCommand) -> None:
        await self._usage_log_repository.log_identify(
            person_id=command.person_id,
            confidence=command.confidence,
            duration_ms=command.duration_ms,
            image_url=command.image_url,
        )

    async def handle_log_register(self, command: LogRegisterCommand) -> None:
        await self._usage_log_repository.log_register(
            person_id=command.person_id,
            duration_ms=command.duration_ms,
        )
