from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    mission_id: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    health: Mapped[Optional[float]] = mapped_column(Float, default=1.0)
    iq: Mapped[Optional[float]] = mapped_column(Float, default=1.0)
    plasticity: Mapped[Optional[float]] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
