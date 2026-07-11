from __future__ import annotations

from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    organization_id: Mapped[Optional[str]] = mapped_column(String(36), index=True)
    type: Mapped[Optional[str]] = mapped_column(String(64))
    manager_id: Mapped[Optional[str]] = mapped_column(String(36))
    name: Mapped[Optional[str]] = mapped_column(String(128))
    description: Mapped[Optional[str]] = mapped_column(Text)
