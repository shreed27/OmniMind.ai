from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    mission_id: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    worker_id: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    kind: Mapped[Optional[str]] = mapped_column(String(64))
    storage_path: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
