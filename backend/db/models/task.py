from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    mission_id: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    worker_id: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    status: Mapped[Optional[str]] = mapped_column(String(32), default="queued")
    confidence: Mapped[Optional[float]] = mapped_column(Float, default=1.0)
    artifact_path: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
