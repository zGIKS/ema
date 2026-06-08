from __future__ import annotations

from uuid import uuid4

from src.app.shared.exceptions import ConflictError, NotFoundError, ValidationError
from src.app.identity.domain.model.commands import (
    AddPersonFaceSamplesCommand,
    RegisterPersonFaceCommand,
)
from src.app.identity.domain.model.entities import PersonAggregate
from src.app.identity.domain.model.results import DniLookupResult
from src.app.identity.domain.model.valueobjects import PersonName, PeruvianDni
from src.app.identity.domain.repositories import PersonRepository
from src.app.biometrics.domain.services import FaceEmbeddingExtractionQueryService
from src.app.identity.application.internal.outboundservices.acl.CloudinaryImageUploadService import (
    CloudinaryImageUploadService,
)
from src.app.identity.domain.services import (
    DniLookupQueryService,
    PersonEnrollmentCommandService,
)


class PersonEnrollmentCommandServiceImpl(PersonEnrollmentCommandService):
    def __init__(
        self,
        *,
        person_repository: PersonRepository,
        extraction_query_service: FaceEmbeddingExtractionQueryService,
        image_upload_service: CloudinaryImageUploadService,
        dni_lookup_query_service: DniLookupQueryService,
        max_embeddings_per_person: int,
        match_threshold: float,
    ) -> None:
        self._person_repository = person_repository
        self._extraction_query_service = extraction_query_service
        self._image_upload_service = image_upload_service
        self._dni_lookup_query_service = dni_lookup_query_service
        self._max_embeddings_per_person = max(1, int(max_embeddings_per_person))
        self._match_threshold = float(match_threshold)

    async def handle_register_face(
        self,
        command: RegisterPersonFaceCommand,
    ) -> PersonAggregate:
        dni = PeruvianDni(command.dni)
        identity = await self._dni_lookup_query_service.handle_lookup_dni(dni)
        if identity is None:
            raise ValidationError("DNI is not eligible for registration")
        if identity.document_number != dni.value:
            raise ValidationError("DNI lookup returned inconsistent data")

        extraction = await self._extraction_query_service.handle_extract_embedding(
            command.image_bytes
        )

        first_name, last_name = self._identity_to_names(identity)
        person = await self._person_repository.find_by_dni(dni)

        if person is not None:
            raise ConflictError("DNI already enrolled")

        image_url = await self._image_upload_service.upload_image(
            image_bytes=command.image_bytes,
            public_id=f"identity/persons/{dni.value}/profile",
            filename=command.image_filename,
            content_type=command.image_content_type,
        )

        aggregate = PersonAggregate.create(
            first_name=first_name,
            last_name=last_name,
            dni=dni,
            image_url=image_url,
        )
        updated = aggregate.add_sample(
            embedding=extraction.embedding,
            image_url=image_url,
            max_samples=self._max_embeddings_per_person,
        )
        return await self._person_repository.save(updated)

    async def handle_add_face_samples(
        self,
        command: AddPersonFaceSamplesCommand,
    ) -> PersonAggregate:
        person = await self._person_repository.find_by_id(command.person_id)
        if person is None:
            raise NotFoundError("Person not found")

        updated = person
        for index, image_bytes in enumerate(command.image_bytes_list, start=1):
            extraction = await self._extraction_query_service.handle_extract_embedding(
                image_bytes
            )
            if not updated.matches_embedding(
                extraction.embedding,
                threshold=self._match_threshold,
            ):
                raise ConflictError("Face does not match the enrolled person")

            image_url = await self._image_upload_service.upload_image(
                image_bytes=image_bytes,
                public_id=f"identity/persons/{person.person_id.value}/samples/{uuid4()}-{index}",
                filename=f"sample-{index}.jpg",
                content_type="application/octet-stream",
            )
            updated = updated.add_sample(
                embedding=extraction.embedding,
                image_url=image_url,
                max_samples=self._max_embeddings_per_person,
            )

        return await self._person_repository.save(updated)

    @staticmethod
    def _identity_to_names(identity: DniLookupResult) -> tuple[PersonName, PersonName]:
        first_name = PersonName(identity.first_name)
        last_name = PersonName(
            f"{identity.first_last_name} {identity.second_last_name}".strip()
        )
        return first_name, last_name
