from __future__ import annotations

import pytest

from kernel.services.constitution import ConstitutionRule, ConstitutionService


def _rule(rule_id: str = "rule-1", *, effective_from: str = "2025-01-01T00:00:00+00:00", effective_to: str | None = None) -> ConstitutionRule:
    return ConstitutionRule(
        rule_id=rule_id,
        organization_id="org-1",
        version="v1",
        rule="no secret in logs",
        effective_from=effective_from,
        effective_to=effective_to,
        status="active",
    )


def test_active_rule_selection() -> None:
    service = ConstitutionService()
    service.propose(_rule())
    rules = service.effective("org-1")
    assert len(rules) == 1
    assert rules[0].rule_id == "rule-1"


def test_rollback_creates_new_revision() -> None:
    service = ConstitutionService()
    service.propose(_rule())
    reissued = service.rollback("org-1", "rule-1", "ceo")
    assert reissued.status == "active"
    assert reissued.source_ref == "rule-1"
    all_rules = service.query("org-1")
    assert any(rule["version"].endswith("-rollback") for rule in all_rules)
