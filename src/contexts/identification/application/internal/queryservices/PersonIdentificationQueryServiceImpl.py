from __future__ import annotations

from src.contexts.identification.domain.model.queries import IdentifyPersonQuery
from src.contexts.identification.domain.model.results import IdentificationResult
from src.contexts.identification.domain.model.valueobjects import ConfidenceScore
from src.contexts.identification.domain.repositories import PersonRepository
from src.contexts.identification.domain.services import (
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
        return IdentificationResult(
            person_id=recognized_person,
            confidence=ConfidenceScore(confidence_value if recognized_person else 0.0),
            box=extraction.box,
        )
