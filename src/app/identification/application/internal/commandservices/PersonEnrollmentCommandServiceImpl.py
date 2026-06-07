from __future__ import annotations

import base64

from src.app.identification.domain.model.commands import RegisterFaceCommand
from src.app.identification.domain.model.entities import PersonAggregate
from src.app.identification.domain.model.events import FaceRegisteredEvent
from src.app.identification.domain.model.valueobjects import PersonName, PeruvianDni
from src.app.identification.domain.repositories import PersonRepository
from src.app.identification.domain.services import (
    FaceEmbeddingExtractionQueryService,
    PersonEnrollmentCommandService,
)


class PersonEnrollmentCommandServiceImpl(PersonEnrollmentCommandService):
    def __init__(
        self,
        *,
        person_repository: PersonRepository,
        extraction_query_service: FaceEmbeddingExtractionQueryService,
        max_embeddings_per_person: int,
    ) -> None:
        self._person_repository = person_repository
        self._extraction_query_service = extraction_query_service
        self._max_embeddings_per_person = max(1, int(max_embeddings_per_person))

    async def handle_register_face(
        self,
        command: RegisterFaceCommand,
    ) -> FaceRegisteredEvent:
        extraction = await self._extraction_query_service.handle_extract_embedding(
            command.image_bytes
        )

        first_name = PersonName(command.first_name)
        last_name = PersonName(command.last_name)
        dni = PeruvianDni(command.dni)
        photo = base64.b64encode(command.image_bytes).decode("ascii")
        person = await self._person_repository.find_by_dni(dni)
        aggregate = (
            person.update_identity(first_name=first_name, last_name=last_name)
            if person is not None
            else PersonAggregate.create(
                first_name=first_name,
                last_name=last_name,
                dni=dni,
                photo=photo,
            )
        )
        updated = aggregate.add_sample(
            embedding=extraction.embedding,
            max_samples=self._max_embeddings_per_person,
            photo=photo,
        )
        await self._person_repository.save(updated)
        return FaceRegisteredEvent(person_id=updated.person_id.value)
