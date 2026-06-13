from __future__ import annotations

from time import perf_counter
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status

from uuid import uuid4

from src.app.biometrics.application.internal.queryservices.PersonIdentificationQueryServiceImpl import (
    PersonIdentificationQueryServiceImpl,
)
from src.app.biometrics.domain.model.queries import IdentifyPersonQuery
from src.app.auditory.interfaces.acl.AuditoryContextFacade import AuditoryContextFacade
from src.app.auditory.interfaces.rest.dependencies import get_auditory_context_facade
from src.app.biometrics.interfaces.rest.resources import IdentificationResponse
from src.app.biometrics.interfaces.rest.dependencies import get_person_identification_query_service
from src.app.iam.domain.model.entities import CurrentUser
from src.app.iam.interfaces.rest.dependencies import get_current_user
from src.app.identity.application.internal.outboundservices.acl.CloudinaryImageUploadService import (
    CloudinaryImageUploadService,
)
from src.app.identity.interfaces.rest.dependencies import (
    get_cloudinary_image_upload_service,
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
    auditory_facade: Annotated[
        AuditoryContextFacade,
        Depends(get_auditory_context_facade),
    ],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    image_upload_service: Annotated[
        CloudinaryImageUploadService,
        Depends(get_cloudinary_image_upload_service),
    ],
    file: UploadFile = File(..., description="Image file that contains one face"),
) -> IdentificationResponse:
    started = perf_counter()
    image_bytes = await file.read()

    # Upload query image to Cloudinary for audit/telemetry
    query_image_url = None
    try:
        query_image_url = await image_upload_service.upload_image(
            image_bytes=image_bytes,
            public_id=f"biometrics/identifications/{uuid4()}/query",
            filename=file.filename,
            content_type=file.content_type,
        )
    except Exception:
        # If upload fails, continue identification flow but log without image_url
        pass

    query = IdentifyPersonQuery(image_bytes=image_bytes)
    identification = await query_service.handle_identify_person(query)

    await auditory_facade.log_identify(
        user_id=current_user.user_id.value,
        person_id=identification.person_id.value if identification.person_id else None,
        first_name=identification.first_name,
        last_name=identification.last_name,
        dni=identification.dni,
        confidence=identification.confidence.value if identification.confidence else None,
        duration_ms=int((perf_counter() - started) * 1000),
        image_url=query_image_url,
    )

    return IdentificationResponse(
        uuid=identification.person_id.value if identification.person_id else None,
        first_name=identification.first_name,
        last_name=identification.last_name,
        dni=identification.dni,
        image_url=identification.image_url,
        confidence=identification.confidence.value if identification.confidence else None,
    )
