from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.contexts.identification.infrastructure.persistence.sqlalchemy.models.BaseModel import (
    BaseModel,
)


class PersonModel(BaseModel):
    __tablename__ = "persons"

    person_id: Mapped[str] = mapped_column(String, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))
    dni: Mapped[str] = mapped_column(String(8), unique=True, index=True)
    created_at: Mapped[int] = mapped_column(Integer)
    updated_at: Mapped[int] = mapped_column(Integer)
