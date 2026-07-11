from __future__ import annotations

from typing import Any

from app.core.events import emit
from app.core.logging import get_logger
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session

logger = get_logger("kernel.services.constitution")


class ConstitutionRule(BaseModel):
    rule_id: str
    effective_from: str
    effective_to: str | None = None
    content: dict[str, Any]


class ConstitutionService:
    def __init__(self, *, session_factory: Any = None) -> None:
        self.session_factory = session_factory or get_session

    async def active_rule(self, rule_id: str, as_of: str) -> ConstitutionRule | None:
        async with self.session_factory() as session:
            result = await session.execute(
                text("""
                SELECT rule_id, effective_from, effective_to, content
                FROM organization_constitutions
                WHERE rule_id = :rule_id
                  AND effective_from <= :as_of
                  AND (effective_to IS NULL OR effective_to > :as_of)
                ORDER BY effective_from DESC
                LIMIT 1
                """),
                {"rule_id": rule_id, "as_of": as_of},
            )
            row = result.mappings().first()
            if not row:
                return None
            return ConstitutionRule(rule_id=row["rule_id"], effective_from=str(row["effective_from"]), effective_to=str(row["effective_to"]) if row["effective_to"] else None, content=row["content"])

    async def rollback(self, rule_id: str, as_of: str) -> ConstitutionRule:
        async with self.session_factory() as session:
            await session.execute(
                text("""
                INSERT INTO organization_constitutions (rule_id, effective_from, effective_to, content)
                VALUES (:rule_id, :now, NULL, :content)
                """),
                {"rule_id": rule_id, "now": as_of, "content": {}},
            )
            await session.commit()
            emit("ConstitutionRolledBack", {"rule_id": rule_id}, {"rule_id": rule_id})
            return ConstitutionRule(rule_id=rule_id, effective_from=as_of, effective_to=None, content={})


__all__ = ["ConstitutionRule", "ConstitutionService"]
