from __future__ import annotations

from src.app.auditory.domain.model.commands.LogAddPersonFaceSamplesCommand import (
    LogAddPersonFaceSamplesCommand,
)
from src.app.auditory.domain.model.commands.LogIdentifyCommand import LogIdentifyCommand
from src.app.auditory.domain.model.commands.LogRegisterCommand import LogRegisterCommand
from src.app.auditory.domain.services.UsageLogCommandService import UsageLogCommandService
from src.app.auditory.interfaces.acl.AuditoryContextFacade import AuditoryContextFacade


class AuditoryContextFacadeImpl(AuditoryContextFacade):
    def __init__(self, *, command_service: UsageLogCommandService) -> None:
        self._command_service = command_service

    async def log_identify(
        self,
        *,
        user_id: str,
        person_id: str | None,
        first_name: str | None = None,
        last_name: str | None = None,
        dni: str | None = None,
        confidence: float | None,
        duration_ms: int,
        image_url: str | None = None,
    ) -> None:
        command = LogIdentifyCommand(
            user_id=user_id,
            person_id=person_id,
            first_name=first_name,
            last_name=last_name,
            dni=dni,
            confidence=confidence,
            duration_ms=duration_ms,
            image_url=image_url,
        )
        await self._command_service.handle_log_identify(command)

    async def log_register(
        self,
        *,
        user_id: str,
        person_id: str,
        first_name: str,
        last_name: str,
        dni: str,
        duration_ms: int,
        image_url: str | None = None,
    ) -> None:
        command = LogRegisterCommand(
            user_id=user_id,
            person_id=person_id,
            first_name=first_name,
            last_name=last_name,
            dni=dni,
            duration_ms=duration_ms,
            image_url=image_url,
        )
        await self._command_service.handle_log_register(command)

    async def log_add_person_face_samples(
        self,
        *,
        user_id: str,
        person_id: str,
        first_name: str,
        last_name: str,
        dni: str,
        samples_added: int,
        total_samples: int,
        duration_ms: int,
    ) -> None:
        command = LogAddPersonFaceSamplesCommand(
            user_id=user_id,
            person_id=person_id,
            first_name=first_name,
            last_name=last_name,
            dni=dni,
            samples_added=samples_added,
            total_samples=total_samples,
            duration_ms=duration_ms,
        )
        await self._command_service.handle_log_add_person_face_samples(command)
