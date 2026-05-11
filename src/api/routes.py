from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile

from src.api.schemas import IdentificationResponse, RegisterResponse
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
    person_id: str = Form(...),
    file: UploadFile = File(...),
) -> RegisterResponse:
    image_bytes = await file.read()
    _service.register_face(person_id=person_id, image_bytes=image_bytes)
    return RegisterResponse(person_id=person_id, enrolled=True)

