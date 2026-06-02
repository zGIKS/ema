from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter, File, Form, UploadFile

from src.api.schemas import IdentificationResponse, RegisterResponse
from src.core.exceptions import ValidationError
from src.services.recognition_service import RecognitionService

router = APIRouter()

# Simple process-wide service wiring (no DI container yet).
_service = RecognitionService.build_default()


@router.post("/identify", response_model=IdentificationResponse)
async def identify(file: UploadFile = File(...)) -> IdentificationResponse:
    image_bytes = await file.read()
    result = _service.identify(image_bytes=image_bytes)
    return IdentificationResponse(
        person_id=result.person_id,
        confidence=result.confidence,
        box=None
        if result.box is None
        else {
            "x": result.box.x,
            "y": result.box.y,
            "w": result.box.w,
            "h": result.box.h,
        },
    )


@router.post("/register", response_model=RegisterResponse)
async def register(
    person_id: str | None = Form(None),
    files: list[UploadFile] | None = File(None),
    file: UploadFile | None = File(None),
) -> RegisterResponse:
    started = perf_counter()
    resolved_person_id = (person_id or "").strip() or uuid4().hex

    uploads: list[UploadFile] = []
    if files:
        uploads.extend(files)
    if file is not None:
        uploads.append(file)
    if not uploads:
        # Keep error shape consistent with our domain errors.
        raise ValidationError("No file(s) uploaded")

    for upl in uploads:
        image_bytes = await upl.read()
        _service.register_face(person_id=resolved_person_id, image_bytes=image_bytes)

    _service.log_register_usage(
        person_id=resolved_person_id,
        duration_ms=int((perf_counter() - started) * 1000),
    )
    return RegisterResponse(person_id=resolved_person_id, enrolled=True)
