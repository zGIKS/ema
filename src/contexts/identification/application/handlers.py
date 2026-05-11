from __future__ import annotations

from dataclasses import dataclass

from src.contexts.identification.application.ports import PersonRepository
from src.contexts.identification.domain.model.commands import (
    IdentifyPersonCommand,
    RegisterFaceCommand,
)
from src.contexts.identification.domain.model.valueobjects import (
    ConfidenceScore,
    PersonId,
)
from src.contexts.identification.domain.services.face_recognition_service import (
    FaceRecognitionService,
)


@dataclass(frozen=True, slots=True)
class IdentificationResult:
    person_id: PersonId | None
    confidence: ConfidenceScore
    box: object | None  # BoundingBox VO, but avoid import cycles in DTO wrapper


class IdentifyPersonCommandHandler:
    def __init__(
        self,
        engine: FaceRecognitionService,
        repo: PersonRepository,
        match_threshold: float,
    ) -> None:
        self._engine = engine
        self._repo = repo
        self._match_threshold = float(match_threshold)

    def handle(self, cmd: IdentifyPersonCommand) -> IdentificationResult:
        extraction = self._engine.extract(cmd.image_bytes)
        match = self._repo.best_match(extraction.embedding)
        if match is None:
            return IdentificationResult(
                person_id=None,
                confidence=ConfidenceScore(0.0),
                box=extraction.box,
            )

        # Convert cosine similarity [-1,1] to confidence-ish [0,1] for API friendliness.
        confidence_value = max(0.0, min(1.0, (match.score + 1.0) / 2.0))
        person = match.person_id if confidence_value >= self._match_threshold else None
        return IdentificationResult(
            person_id=person,
            confidence=ConfidenceScore(confidence_value if person else 0.0),
            box=extraction.box,
        )


class RegisterFaceCommandHandler:
    def __init__(self, engine: FaceRecognitionService, repo: PersonRepository) -> None:
        self._engine = engine
        self._repo = repo

    def handle(self, cmd: RegisterFaceCommand) -> None:
        extraction = self._engine.extract(cmd.image_bytes)
        self._repo.upsert_embedding(PersonId(cmd.person_id), extraction.embedding)

