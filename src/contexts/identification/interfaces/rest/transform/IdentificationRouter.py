from __future__ import annotations

from time import perf_counter
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from src.contexts.identification.application.internal.commandservices.PersonEnrollmentCommandServiceImpl import (
    PersonEnrollmentCommandServiceImpl,
)
from src.contexts.identification.application.internal.queryservices.PersonIdentificationQueryServiceImpl import (
    PersonIdentificationQueryServiceImpl,
)
from src.contexts.identification.domain.model.commands import RegisterFaceCommand
from src.contexts.identification.domain.model.queries import IdentifyPersonQuery
from src.contexts.identification.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemyUsageLogRepository,
)
from src.contexts.identification.interfaces.rest.dependencies import (
    get_person_enrollment_command_service,
    get_person_identification_query_service,
    get_usage_log_repository,
)
from src.contexts.identification.interfaces.rest.resources import (
    BoundingBoxResource,
    ErrorResponse,
    IdentificationResponse,
    RegisterResponse,
)
from src.core.exceptions import ValidationError

router = APIRouter(
    prefix="/api/v1/identification",
    tags=["Identification"],
)


@router.post(
    "/identify",
    response_model=IdentificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Identify person by face image",
    description="Extracts face embedding from the uploaded image and returns the best matched person.",
    responses={
        200: {"description": "Identification evaluated successfully"},
        404: {"model": ErrorResponse, "description": "No face detected in image"},
        422: {
            "model": ErrorResponse,
            "description": "Input validation failed (empty file or invalid image)",
        },
    },
)
async def identify_person(
    query_service: Annotated[
        PersonIdentificationQueryServiceImpl,
        Depends(get_person_identification_query_service),
    ],
    usage_log_repository: Annotated[
        SqlAlchemyUsageLogRepository,
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

    resource_box = (
        None
        if identification.box is None
        else BoundingBoxResource(
            x=identification.box.x,
            y=identification.box.y,
            w=identification.box.w,
            h=identification.box.h,
        )
    )
    return IdentificationResponse(
        person_id=identification.person_id.value if identification.person_id else None,
        confidence=identification.confidence.value,
        box=resource_box,
    )


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll person face samples",
    description="Registers one or many face images for a person using first name, last name and Peruvian DNI. The UUID person id is generated and managed internally.",
    responses={
        201: {"description": "Face samples enrolled"},
        422: {
            "model": ErrorResponse,
            "description": "No files provided or invalid input payload",
        },
    },
)
async def register_person_face(
    command_service: Annotated[
        PersonEnrollmentCommandServiceImpl,
        Depends(get_person_enrollment_command_service),
    ],
    usage_log_repository: Annotated[
        SqlAlchemyUsageLogRepository,
        Depends(get_usage_log_repository),
    ],
    first_name: str = Form(
        ...,
        description="Person first name. Allows Spanish letters, spaces, enie and accents only.",
        examples=["Jose Luis"],
    ),
    last_name: str = Form(
        ...,
        description="Person last name. Allows Spanish letters, spaces, enie and accents only.",
        examples=["Quispe Nunez"],
    ),
    dni: str = Form(
        ...,
        description="Peruvian DNI. Must contain exactly 8 digits.",
        examples=["12345678"],
    ),
    files: list[UploadFile] | None = File(
        default=None,
        description="Optional list of image files. Repeat the 'files' field to send many.",
    ),
    file: UploadFile | None = File(
        default=None,
        description="Optional single image file. Can be used together with files[] input.",
    ),
) -> RegisterResponse:
    started = perf_counter()

    uploads: list[UploadFile] = []
    if files:
        uploads.extend(files)
    if file is not None:
        uploads.append(file)
    if not uploads:
        raise ValidationError("No file(s) uploaded")

    for upload in uploads:
        image_bytes = await upload.read()
        command = RegisterFaceCommand(
            first_name=first_name,
            last_name=last_name,
            dni=dni,
            image_bytes=image_bytes,
        )
        event = await command_service.handle_register_face(command)

    await usage_log_repository.log_register(
        person_id=event.person_id,
        duration_ms=int((perf_counter() - started) * 1000),
    )

    return RegisterResponse(
        first_name=" ".join(first_name.strip().split()),
        last_name=" ".join(last_name.strip().split()),
        dni=dni.strip(),
        enrolled=True,
    )
