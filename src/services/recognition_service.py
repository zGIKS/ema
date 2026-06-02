from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from src.contexts.identification.application.handlers import (
    IdentifyPersonCommandHandler,
    RegisterFaceCommandHandler,
)
from src.contexts.identification.domain.model.commands import (
    IdentifyPersonCommand,
    RegisterFaceCommand,
)
from src.contexts.identification.infrastructure.ai.stub_engine import StubFaceRecognitionEngine
from src.contexts.identification.infrastructure.persistence.sqlite_repo import (
    SQLitePersonRepository,
)
from src.contexts.identification.infrastructure.persistence.sqlite_usage_log_repo import (
    SQLiteUsageLogRepository,
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
        usage_log_repo: SQLiteUsageLogRepository,
    ) -> None:
        self._identify = identify_handler
        self._register = register_handler
        self._usage_logs = usage_log_repo

    @staticmethod
    def build_default() -> "RecognitionService":
        # MVP default: persist embeddings in SQLite.
        # For ephemeral/dev usage you can swap back to InMemoryPersonRepository.
        repo = SQLitePersonRepository(
            db_path=settings.db_path,
            max_embeddings_per_person=settings.max_embeddings_per_person,
        )
        usage_logs = SQLiteUsageLogRepository(db_path=settings.db_path)
        engine = _build_engine()
        identify = IdentifyPersonCommandHandler(
            engine=engine,
            repo=repo,
            match_threshold=settings.match_threshold,
        )
        register = RegisterFaceCommandHandler(engine=engine, repo=repo)
        return RecognitionService(
            identify_handler=identify,
            register_handler=register,
            usage_log_repo=usage_logs,
        )

    def identify(self, image_bytes: bytes) -> IdentificationResultDTO:
        started = perf_counter()
        cmd = IdentifyPersonCommand(image_bytes=image_bytes)
        res = self._identify.handle(cmd)
        duration_ms = int((perf_counter() - started) * 1000)
        self._usage_logs.log_identify(
            person_id=res.person_id.value if res.person_id else None,
            confidence=res.confidence.value,
            duration_ms=duration_ms,
        )
        return IdentificationResultDTO(
            person_id=res.person_id.value if res.person_id else None,
            confidence=res.confidence.value,
            box=res.box,
        )

    def register_face(self, person_id: str, image_bytes: bytes) -> None:
        cmd = RegisterFaceCommand(person_id=person_id, image_bytes=image_bytes)
        self._register.handle(cmd)

    def log_register_usage(self, *, person_id: str, duration_ms: int) -> None:
        self._usage_logs.log_register(person_id=person_id, duration_ms=duration_ms)


def _build_engine():
    engine_setting = (settings.engine or "auto").strip().lower()
    if engine_setting not in {"auto", "stub", "insightface"}:
        engine_setting = "auto"

    if engine_setting == "stub":
        return StubFaceRecognitionEngine()

    if engine_setting in {"auto", "insightface"}:
        try:
            from src.contexts.identification.infrastructure.ai.insightface_engine import (
                InsightFaceRecognitionEngine,
            )

            return InsightFaceRecognitionEngine(
                model_name=settings.insightface_model,
                det_size=settings.insightface_det_size,
            )
        except Exception:
            if engine_setting == "insightface":
                raise
            return StubFaceRecognitionEngine()

    return StubFaceRecognitionEngine()
