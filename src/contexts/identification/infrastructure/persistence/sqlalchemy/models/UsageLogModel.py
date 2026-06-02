from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.contexts.identification.infrastructure.persistence.sqlalchemy.models.BaseModel import (
    BaseModel,
)


class UsageLogModel(BaseModel):
    __tablename__ = "usage_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    operation: Mapped[str] = mapped_column(String, index=True)
    person_id: Mapped[str | None] = mapped_column(String, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer)
    used_at: Mapped[int] = mapped_column(Integer, index=True)
