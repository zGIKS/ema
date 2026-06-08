from __future__ import annotations

from typing import Protocol

from src.app.auditory.domain.model.commands.LogAddPersonFaceSamplesCommand import (
    LogAddPersonFaceSamplesCommand,
)
from src.app.auditory.domain.model.commands.LogIdentifyCommand import LogIdentifyCommand
from src.app.auditory.domain.model.commands.LogRegisterCommand import LogRegisterCommand


class UsageLogCommandService(Protocol):
    async def handle_log_identify(self, command: LogIdentifyCommand) -> None:
        ...

    async def handle_log_register(self, command: LogRegisterCommand) -> None:
        ...

    async def handle_log_add_person_face_samples(
        self,
        command: LogAddPersonFaceSamplesCommand,
    ) -> None:
        ...
