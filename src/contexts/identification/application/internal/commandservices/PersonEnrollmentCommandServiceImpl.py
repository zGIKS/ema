from __future__ import annotations

from src.contexts.identification.domain.model.commands import RegisterFaceCommand
from src.contexts.identification.domain.model.entities import PersonAggregate
from src.contexts.identification.domain.model.events import FaceRegisteredEvent
from src.contexts.identification.domain.model.valueobjects import PersonId
from src.contexts.identification.domain.repositories import PersonRepository
from src.contexts.identification.domain.services import (
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

        person_id = PersonId(command.person_id)
        person = await self._person_repository.find_by_id(person_id)
        aggregate = person if person is not None else PersonAggregate.create(person_id)
        updated = aggregate.add_sample(
            embedding=extraction.embedding,
            max_samples=self._max_embeddings_per_person,
        )
        await self._person_repository.save(updated)
        return FaceRegisteredEvent(person_id=person_id.value)
