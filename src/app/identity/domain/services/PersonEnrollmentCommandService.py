from __future__ import annotations

from typing import Protocol

from src.app.identity.domain.model.commands import (
    AddPersonFaceSamplesCommand,
    RegisterPersonFaceCommand,
)
from src.app.identity.domain.model.entities import PersonAggregate


class PersonEnrollmentCommandService(Protocol):
    async def handle_register_face(
        self,
        command: RegisterPersonFaceCommand,
    ) -> PersonAggregate:
        ...

    async def handle_add_face_samples(
        self,
        command: AddPersonFaceSamplesCommand,
    ) -> PersonAggregate:
        ...
