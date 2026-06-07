from __future__ import annotations

from typing import Protocol

from src.app.identification.domain.model.commands import RegisterFaceCommand
from src.app.identification.domain.model.events import FaceRegisteredEvent


class PersonEnrollmentCommandService(Protocol):
    async def handle_register_face(
        self,
        command: RegisterFaceCommand,
    ) -> FaceRegisteredEvent:
        ...
