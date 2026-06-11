from __future__ import annotations

from sqlalchemy import BigInteger, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.app.shared.infrastructure.persistence.sqlalchemy.base import Base


class UsageLogModel(Base):
    __tablename__ = "usage_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    operation: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    person_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    dni: Mapped[str | None] = mapped_column(String(20), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    samples_added: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_samples: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    used_at: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
