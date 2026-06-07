from __future__ import annotations

from typing import Protocol

from src.app.identification.domain.model.commands import (
    AddPersonFaceSamplesCommand,
    RegisterFaceCommand,
)
from src.app.identification.domain.model.events import FaceRegisteredEvent
from src.app.identification.domain.model.entities import PersonAggregate


class PersonEnrollmentCommandService(Protocol):
    async def handle_register_face(
        self,
        command: RegisterFaceCommand,
    ) -> FaceRegisteredEvent:
        ...

    async def handle_add_face_samples(
        self,
        command: AddPersonFaceSamplesCommand,
    ) -> PersonAggregate:
        ...
