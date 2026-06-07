from __future__ import annotations

from time import perf_counter
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from src.app.identity.application.internal.commandservices.PersonEnrollmentCommandServiceImpl import (
    PersonEnrollmentCommandServiceImpl,
)
from src.app.identity.domain.model.commands import (
    AddPersonFaceSamplesCommand,
    RegisterPersonFaceCommand,
)
from src.app.identity.domain.model.valueobjects import PersonId
from src.app.identity.interfaces.rest.resources import (
    AddFaceSamplesResponse,
    RegisterResponse,
    RegisteredPersonResource,
    RegisteredPersonsPageResponse,
)
from src.app.identity.domain.model.queries.GetRegisteredPersonsQuery import (
    GetRegisteredPersonsQuery,
)
from src.app.identity.application.internal.queryservices.PersonDirectoryQueryServiceImpl import (
    PersonDirectoryQueryServiceImpl,
)
from src.app.identity.infrastructure.persistence.mongodb.repositories.MongoDbUsageLogRepository import (
    MongoDbUsageLogRepository,
)
from src.app.identity.interfaces.rest.dependencies import (
    get_person_directory_query_service,
    get_person_enrollment_command_service,
    get_usage_log_repository,
)
from src.app.shared.interfaces.rest.resources import ErrorResponse
from src.app.shared.exceptions import ValidationError

router = APIRouter(prefix="/api/v1/identity", tags=["Identity"])


@router.get(
    "/persons",
    response_model=RegisteredPersonsPageResponse,
    status_code=status.HTTP_200_OK,
    summary="List registered persons",
    description="Returns the registered persons with safe fields only.",
)
async def get_registered_persons(
    query_service: Annotated[
        PersonDirectoryQueryServiceImpl,
        Depends(get_person_directory_query_service),
    ],
    page: int = 1,
    page_size: int = 20,
) -> RegisteredPersonsPageResponse:
    query = GetRegisteredPersonsQuery(page=page, page_size=page_size)
    persons_page = await query_service.handle_get_registered_persons(query)

    return RegisteredPersonsPageResponse(
        items=[
            RegisteredPersonResource(
                uuid=person.person_id.value,
                first_name=person.first_name.value,
                last_name=person.last_name.value,
                dni=person.dni.value,
                image_url=person.image_url,
            )
            for person in persons_page.items
        ],
        page=persons_page.page,
        page_size=persons_page.page_size,
        total=persons_page.total,
    )


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a person",
    description="Creates a person using DNI + one face image.",
    responses={
        201: {"description": "Person registered successfully"},
        409: {"model": ErrorResponse, "description": "DNI already exists"},
        422: {"model": ErrorResponse, "description": "Invalid request"},
    },
)
async def register_person_face(
    command_service: Annotated[
        PersonEnrollmentCommandServiceImpl,
        Depends(get_person_enrollment_command_service),
    ],
    usage_log_repository: Annotated[
        MongoDbUsageLogRepository,
        Depends(get_usage_log_repository),
    ],
    dni: str = Form(..., description="Peruvian DNI", examples=["12345678"]),
    file: UploadFile = File(..., description="Single image file"),
) -> RegisterResponse:
    started = perf_counter()

    image_bytes = await file.read()
    person = await command_service.handle_register_face(
        RegisterPersonFaceCommand(
            dni=dni,
            image_bytes=image_bytes,
            image_filename=file.filename,
            image_content_type=file.content_type,
        )
    )

    await usage_log_repository.log_register(
        person_id=person.person_id.value,
        duration_ms=int((perf_counter() - started) * 1000),
    )

    return RegisterResponse(
        first_name=person.first_name.value,
        last_name=person.last_name.value,
        dni=person.dni.value,
        enrolled=True,
    )


@router.post(
    "/persons/{person_id}/samples",
    response_model=AddFaceSamplesResponse,
    status_code=status.HTTP_200_OK,
    summary="Add face samples",
    description="Adds more photos to an existing person without changing identity data.",
    responses={
        200: {"description": "Samples added successfully"},
        404: {"model": ErrorResponse, "description": "Person not found"},
        409: {
            "model": ErrorResponse,
            "description": "Uploaded face does not match the enrolled person",
        },
        422: {"model": ErrorResponse, "description": "Invalid request"},
    },
)
async def add_person_face_samples(
    command_service: Annotated[
        PersonEnrollmentCommandServiceImpl,
        Depends(get_person_enrollment_command_service),
    ],
    person_id: str,
    files: list[UploadFile] | None = File(default=None),
    file: UploadFile | None = File(default=None),
) -> AddFaceSamplesResponse:
    uploads: list[UploadFile] = []
    if files:
        uploads.extend(files)
    if file is not None:
        uploads.append(file)
    if not uploads:
        raise ValidationError("No file(s) uploaded")

    command = AddPersonFaceSamplesCommand(
        person_id=PersonId(person_id),
        image_bytes_list=tuple([await upload.read() for upload in uploads]),
    )
    person = await command_service.handle_add_face_samples(command)

    return AddFaceSamplesResponse(person_id=person.person_id.value, total_samples=len(person.samples))
