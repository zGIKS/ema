from __future__ import annotations

from sqlalchemy import Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from src.app.identity.infrastructure.persistence.sqlalchemy.models.BaseModel import (
    BaseModel,
)


class PersonEmbeddingModel(BaseModel):
    __tablename__ = "embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    person_id: Mapped[str] = mapped_column(String, index=True)
    embedding: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[int] = mapped_column(Integer)
