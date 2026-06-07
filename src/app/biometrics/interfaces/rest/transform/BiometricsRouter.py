from __future__ import annotations

from time import perf_counter
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status

from src.app.biometrics.application.internal.queryservices.PersonIdentificationQueryServiceImpl import (
    PersonIdentificationQueryServiceImpl,
)
from src.app.biometrics.domain.model.queries import IdentifyPersonQuery
from src.app.identity.infrastructure.persistence.mongodb.repositories.MongoDbUsageLogRepository import (
    MongoDbUsageLogRepository,
)
from src.app.biometrics.interfaces.rest.resources import IdentificationResponse
from src.app.biometrics.interfaces.rest.dependencies import (
    get_person_identification_query_service,
    get_usage_log_repository,
)
from src.app.shared.interfaces.rest.resources import ErrorResponse

router = APIRouter(prefix="/api/v1/biometrics", tags=["Biometrics"])


@router.post(
    "/identify",
    response_model=IdentificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Identify a person",
    description="Matches a face image against enrolled biometric samples.",
    responses={
        200: {"description": "Identification evaluated successfully"},
        404: {"model": ErrorResponse, "description": "No face detected in image"},
        422: {"model": ErrorResponse, "description": "Invalid request"},
    },
)
async def identify_person(
    query_service: Annotated[
        PersonIdentificationQueryServiceImpl,
        Depends(get_person_identification_query_service),
    ],
    usage_log_repository: Annotated[
        MongoDbUsageLogRepository,
        Depends(get_usage_log_repository),
    ],
    file: UploadFile = File(..., description="Image file that contains one face"),
) -> IdentificationResponse:
    started = perf_counter()
    image_bytes = await file.read()
    query = IdentifyPersonQuery(image_bytes=image_bytes)
    identification = await query_service.handle_identify_person(query)

    await usage_log_repository.log_identify(
        person_id=identification.person_id.value if identification.person_id else None,
        confidence=identification.confidence.value,
        duration_ms=int((perf_counter() - started) * 1000),
    )

    return IdentificationResponse(
        uuid=identification.person_id.value if identification.person_id else None,
        first_name=identification.first_name,
        last_name=identification.last_name,
        dni=identification.dni,
        image_url=identification.image_url,
        confidence=identification.confidence.value,
    )
