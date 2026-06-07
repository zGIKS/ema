from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

import numpy as np

from src.app.identity.domain.model.entities.FaceSample import FaceSample
from src.app.biometrics.domain.model.valueobjects import FaceEmbedding
from src.app.identity.domain.model.valueobjects.PersonId import PersonId
from src.app.identity.domain.model.valueobjects.PersonName import PersonName
from src.app.identity.domain.model.valueobjects.PeruvianDni import PeruvianDni
from src.app.shared.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class PersonAggregate:
    person_id: PersonId
    first_name: PersonName
    last_name: PersonName
    dni: PeruvianDni
    image_url: str | None
    samples: tuple[FaceSample, ...]

    def __post_init__(self) -> None:
        if self.image_url is not None and not self.image_url.strip():
            raise ValidationError("image_url cannot be empty")

    @staticmethod
    def create(
        *,
        first_name: PersonName,
        last_name: PersonName,
        dni: PeruvianDni,
        image_url: str | None = None,
    ) -> "PersonAggregate":
        return PersonAggregate(
            person_id=PersonId(str(uuid4())),
            first_name=first_name,
            last_name=last_name,
            dni=dni,
            image_url=image_url,
            samples=tuple(),
        )

    def add_sample(
        self,
        embedding: FaceEmbedding,
        max_samples: int,
    ) -> "PersonAggregate":
        appended = (*self.samples, FaceSample(embedding=embedding))
        if max_samples > 0 and len(appended) > max_samples:
            appended = appended[-max_samples:]
        return PersonAggregate(
            person_id=self.person_id,
            first_name=self.first_name,
            last_name=self.last_name,
            dni=self.dni,
            image_url=self.image_url,
            samples=tuple(appended),
        )

    def matches_embedding(self, embedding: FaceEmbedding, threshold: float) -> bool:
        if not self.samples:
            return False

        candidate = np.asarray(embedding.values, dtype=np.float32).reshape(-1)
        candidate /= max(1e-6, float(np.linalg.norm(candidate)))

        best_similarity = -1.0
        for sample in self.samples:
            current = np.asarray(sample.embedding.values, dtype=np.float32).reshape(-1)
            current /= max(1e-6, float(np.linalg.norm(current)))
            similarity = float(np.dot(candidate, current))
            if similarity > best_similarity:
                best_similarity = similarity

        return best_similarity >= float(threshold)
