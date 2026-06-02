from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from src.contexts.identification.domain.model.entities.FaceSample import FaceSample
from src.contexts.identification.domain.model.valueobjects import (
    FaceEmbedding,
    PersonId,
    PersonName,
    PeruvianDni,
)


@dataclass(frozen=True, slots=True)
class PersonAggregate:
    person_id: PersonId
    first_name: PersonName
    last_name: PersonName
    dni: PeruvianDni
    samples: tuple[FaceSample, ...]

    @staticmethod
    def create(
        *,
        first_name: PersonName,
        last_name: PersonName,
        dni: PeruvianDni,
    ) -> "PersonAggregate":
        return PersonAggregate(
            person_id=PersonId(str(uuid4())),
            first_name=first_name,
            last_name=last_name,
            dni=dni,
            samples=tuple(),
        )

    def add_sample(self, embedding: FaceEmbedding, max_samples: int) -> "PersonAggregate":
        appended = (*self.samples, FaceSample(embedding=embedding))
        if max_samples > 0 and len(appended) > max_samples:
            appended = appended[-max_samples:]
        return PersonAggregate(
            person_id=self.person_id,
            first_name=self.first_name,
            last_name=self.last_name,
            dni=self.dni,
            samples=tuple(appended),
        )

    def update_identity(
        self,
        *,
        first_name: PersonName,
        last_name: PersonName,
    ) -> "PersonAggregate":
        return PersonAggregate(
            person_id=self.person_id,
            first_name=first_name,
            last_name=last_name,
            dni=self.dni,
            samples=self.samples,
        )
