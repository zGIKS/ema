from __future__ import annotations

from dataclasses import dataclass

from src.app.biometrics.domain.model.valueobjects import FaceEmbedding


@dataclass(frozen=True, slots=True)
class FaceSample:
    embedding: FaceEmbedding
    image_url: str | None = None

    def __post_init__(self) -> None:
        if self.image_url is not None and not self.image_url.strip():
            raise ValueError("image_url cannot be empty")
