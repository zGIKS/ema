from __future__ import annotations

from uuid import uuid4

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.app.shared.infrastructure.persistence.sqlalchemy.base import Base
from src.app.shared.infrastructure.persistence.sqlalchemy.mixins import TimestampMixin


class PersonModel(TimestampMixin, Base):
    __tablename__ = "persons"

    person_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    dni: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    samples: Mapped[list[dict[str, object]]] = mapped_column(JSONB, nullable=False, default=list)
