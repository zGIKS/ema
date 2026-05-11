from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import tempfile
import shutil
from pathlib import Path

from src.services.recognition_service import RecognitionService
from src.models.detector import FaceDetector
from src.models.registry import FaceRegistry
from src.api.schemas import (
    DetectResponse,
    EnrollRequest,
    EnrollResponse,
    IdentifyResponse,
    PersonSummary,
)
from src.core.exceptions import FaceRecognitionError

router = APIRouter()


def get_detector() -> FaceDetector:
    return FaceDetector()


def get_registry() -> FaceRegistry:
    return FaceRegistry()


def get_service(
    detector: FaceDetector = Depends(get_detector),
    registry: FaceRegistry = Depends(get_registry),
) -> RecognitionService:
    return RecognitionService(detector, registry)


@router.post("/detect", response_model=DetectResponse)
async def detect(
    file: UploadFile = File(...),
    service: RecognitionService = Depends(get_service),
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
    try:
        return await service.detect(tmp_path)
    except FaceRecognitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        tmp_path.unlink(missing_ok=True)


@router.post("/enroll", response_model=EnrollResponse)
async def enroll(
    name: str,
    file: UploadFile = File(...),
    service: RecognitionService = Depends(get_service),
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
    try:
        return await service.enroll(tmp_path, name, {})
    except FaceRecognitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        tmp_path.unlink(missing_ok=True)


@router.post("/identify", response_model=List[IdentifyResponse])
async def identify(
    file: UploadFile = File(...),
    service: RecognitionService = Depends(get_service),
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
    try:
        return await service.identify(tmp_path)
    except FaceRecognitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        tmp_path.unlink(missing_ok=True)


@router.get("/persons", response_model=List[PersonSummary])
async def list_persons(service: RecognitionService = Depends(get_service)):
    return await service.list_persons()


@router.delete("/persons/{person_id}")
async def delete_person(person_id: str, service: RecognitionService = Depends(get_service)):
    try:
        await service.delete_person(person_id)
        return {"message": "Persona eliminada correctamente."}
    except FaceRecognitionError as e:
        raise HTTPException(status_code=404, detail=str(e))
