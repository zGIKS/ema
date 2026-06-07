from __future__ import annotations

import base64

from src.app.shared.exceptions import ConflictError, NotFoundError, ValidationError
from src.app.identification.domain.model.commands import (
    AddPersonFaceSamplesCommand,
    RegisterPersonFaceCommand,
)
from src.app.identification.domain.model.entities import PersonAggregate
from src.app.identification.domain.model.results import DniLookupResult
from src.app.identification.domain.model.valueobjects import PersonName, PeruvianDni
from src.app.identification.domain.repositories import PersonRepository
from src.app.identification.domain.services import (
    DniLookupQueryService,
    FaceEmbeddingExtractionQueryService,
    PersonEnrollmentCommandService,
)


class PersonEnrollmentCommandServiceImpl(PersonEnrollmentCommandService):
    def __init__(
        self,
        *,
        person_repository: PersonRepository,
        extraction_query_service: FaceEmbeddingExtractionQueryService,
        dni_lookup_query_service: DniLookupQueryService,
        max_embeddings_per_person: int,
    ) -> None:
        self._person_repository = person_repository
        self._extraction_query_service = extraction_query_service
        self._dni_lookup_query_service = dni_lookup_query_service
        self._max_embeddings_per_person = max(1, int(max_embeddings_per_person))

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
        photo = base64.b64encode(command.image_bytes).decode("ascii")
        person = await self._person_repository.find_by_dni(dni)

        if person is not None:
            raise ConflictError("DNI already enrolled")

        aggregate = PersonAggregate.create(
            first_name=first_name,
            last_name=last_name,
            dni=dni,
            photo=photo,
        )
        updated = aggregate.add_sample(
            embedding=extraction.embedding,
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
        for image_bytes in command.image_bytes_list:
            extraction = await self._extraction_query_service.handle_extract_embedding(
                image_bytes
            )
            updated = updated.add_sample(
                embedding=extraction.embedding,
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
