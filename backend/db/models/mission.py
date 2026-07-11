from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Mission(Base):
    __tablename__ = "missions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[Optional[str]] = mapped_column(String(32), default="created", server_default="created")
    priority: Mapped[Optional[str]] = mapped_column(String(32), default="normal")
    confidence: Mapped[Optional[float]] = mapped_column(default=1.0)
    budget: Mapped[Optional[float]] = mapped_column(default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("status", "created")
        kwargs.setdefault("priority", "normal")
        kwargs.setdefault("confidence", 1.0)
        kwargs.setdefault("budget", 0.0)
        kwargs.setdefault("created_at", datetime.utcnow())
        super().__init__(**kwargs)
