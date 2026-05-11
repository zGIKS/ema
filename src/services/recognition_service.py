from __future__ import annotations

from dataclasses import dataclass

from src.contexts.identification.application.handlers import (
    IdentifyPersonCommandHandler,
    RegisterFaceCommandHandler,
)
from src.contexts.identification.domain.model.commands import (
    IdentifyPersonCommand,
    RegisterFaceCommand,
)
from src.contexts.identification.infrastructure.ai.stub_engine import StubFaceRecognitionEngine
from src.contexts.identification.infrastructure.persistence.in_memory_repo import (
    InMemoryPersonRepository,
)
from src.core.config import settings


@dataclass(frozen=True)
class IdentificationResultDTO:
    person_id: str | None
    confidence: float
    box: object | None  # BoundingBox VO, but keep API layer independent.


class RecognitionService:
    """
    Thin facade for the web layer.
    Internally uses the bounded context's application services.
    """

    def __init__(
        self,
        identify_handler: IdentifyPersonCommandHandler,
        register_handler: RegisterFaceCommandHandler,
    ) -> None:
        self._identify = identify_handler
        self._register = register_handler

    @staticmethod
    def build_default() -> "RecognitionService":
        repo = InMemoryPersonRepository()
        engine = StubFaceRecognitionEngine()
        identify = IdentifyPersonCommandHandler(
            engine=engine,
            repo=repo,
            match_threshold=settings.match_threshold,
        )
        register = RegisterFaceCommandHandler(engine=engine, repo=repo)
        return RecognitionService(identify_handler=identify, register_handler=register)

    def identify(self, image_bytes: bytes) -> IdentificationResultDTO:
        cmd = IdentifyPersonCommand(image_bytes=image_bytes)
        res = self._identify.handle(cmd)
        return IdentificationResultDTO(
            person_id=res.person_id.value if res.person_id else None,
            confidence=res.confidence.value,
            box=res.box,
        )

    def register_face(self, person_id: str, image_bytes: bytes) -> None:
        cmd = RegisterFaceCommand(person_id=person_id, image_bytes=image_bytes)
        self._register.handle(cmd)

