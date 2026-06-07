from __future__ import annotations

from src.app.identification.domain.model.queries import IdentifyPersonQuery
from src.app.identification.domain.model.results import IdentificationResult
from src.app.identification.domain.model.valueobjects import ConfidenceScore
from src.app.identification.domain.repositories import PersonRepository
from src.app.identification.domain.services import (
    FaceEmbeddingExtractionQueryService,
    PersonIdentificationQueryService,
)


class PersonIdentificationQueryServiceImpl(PersonIdentificationQueryService):
    def __init__(
        self,
        *,
        person_repository: PersonRepository,
        extraction_query_service: FaceEmbeddingExtractionQueryService,
        match_threshold: float,
    ) -> None:
        self._person_repository = person_repository
        self._extraction_query_service = extraction_query_service
        self._match_threshold = float(match_threshold)

    async def handle_identify_person(self, query: IdentifyPersonQuery) -> IdentificationResult:
        extraction = await self._extraction_query_service.handle_extract_embedding(
            query.image_bytes
        )
        match = await self._person_repository.find_best_match(extraction.embedding)

        if match is None:
            return IdentificationResult(
                person_id=None,
                first_name=None,
                last_name=None,
                dni=None,
                photo=None,
                confidence=ConfidenceScore(0.0),
                box=extraction.box,
            )

        recognized_person = (
            match.person_id if match.similarity.value >= self._match_threshold else None
        )
        confidence_value = max(
            0.0,
            min(1.0, (match.similarity.value + 1.0) / 2.0),
        )
        person = (
            await self._person_repository.find_by_id(match.person_id)
            if recognized_person is not None
            else None
        )
        return IdentificationResult(
            person_id=recognized_person,
            first_name=person.first_name.value if person is not None else None,
            last_name=person.last_name.value if person is not None else None,
            dni=person.dni.value if person is not None else None,
            photo=person.photo if person is not None else None,
            confidence=ConfidenceScore(confidence_value if recognized_person else 0.0),
            box=extraction.box,
        )
