from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ConstitutionRule:
    rule_id: str
    organization_id: str
    version: str
    rule: str
    effective_from: str
    effective_to: str | None
    status: str
    source_ref: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "organization_id": self.organization_id,
            "version": self.version,
            "rule": self.rule,
            "effective_from": self.effective_from,
            "effective_to": self.effective_to,
            "status": self.status,
            "source_ref": self.source_ref,
        }

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class ConstitutionService:
    def __init__(self) -> None:
        self._rules: list[ConstitutionRule] = []

    def propose(self, rule: ConstitutionRule) -> None:
        self._rules.append(rule)

    def effective(self, organization_id: str) -> list[ConstitutionRule]:
        return [rule for rule in self._rules if rule.organization_id == organization_id and rule.status == "active"]

    def rollback(self, organization_id: str, rule_id: str, role: str) -> ConstitutionRule:
        original = next(rule for rule in self._rules if rule.rule_id == rule_id and rule.organization_id == organization_id)
        rolled_back = ConstitutionRule(
            rule_id=f"{rule_id}-rollback",
            organization_id=organization_id,
            version=f"{original.version}-rollback",
            rule=original.rule,
            effective_from=original.effective_from,
            effective_to=None,
            status="active",
            source_ref=rule_id,
        )
        self._rules.append(rolled_back)
        return rolled_back

    def query(self, organization_id: str) -> list[dict[str, Any]]:
        return [rule.to_dict() for rule in self._rules if rule.organization_id == organization_id]
