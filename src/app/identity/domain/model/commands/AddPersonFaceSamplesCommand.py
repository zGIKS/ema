from __future__ import annotations

from dataclasses import dataclass

from src.app.shared.exceptions import ValidationError
from src.app.identity.domain.model.valueobjects import PersonId


@dataclass(frozen=True, slots=True)
class AddPersonFaceSamplesCommand:
    person_id: PersonId
    image_bytes_list: tuple[bytes, ...]

    def __post_init__(self) -> None:
        if not self.image_bytes_list:
            raise ValidationError("image_bytes_list cannot be empty")

        for image_bytes in self.image_bytes_list:
            if not image_bytes:
                raise ValidationError("image_bytes cannot be empty")
