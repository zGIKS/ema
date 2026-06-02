from __future__ import annotations

from dataclasses import dataclass

from src.contexts.identification.domain.model.entities.FaceSample import FaceSample
from src.contexts.identification.domain.model.valueobjects import FaceEmbedding, PersonId


@dataclass(frozen=True, slots=True)
class PersonAggregate:
    person_id: PersonId
    samples: tuple[FaceSample, ...]

    @staticmethod
    def create(person_id: PersonId) -> "PersonAggregate":
        return PersonAggregate(person_id=person_id, samples=tuple())

    def add_sample(self, embedding: FaceEmbedding, max_samples: int) -> "PersonAggregate":
        appended = (*self.samples, FaceSample(embedding=embedding))
        if max_samples > 0 and len(appended) > max_samples:
            appended = appended[-max_samples:]
        return PersonAggregate(person_id=self.person_id, samples=tuple(appended))
