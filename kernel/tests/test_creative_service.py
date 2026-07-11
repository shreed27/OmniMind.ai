"""Tests for Creative Service - TASK-14.2"""

from __future__ import annotations

import pytest

from kernel.core.event_bus import InMemoryEventBus
from kernel.services.creative_service import CreativeAssetType, CreativeService


@pytest.mark.asyncio
async def test_creative_generation() -> None:
    """Creative service generates assets with variations."""
    bus = InMemoryEventBus()
    creative = CreativeService(event_bus=bus)

    result = await creative.generate(
        asset_type=CreativeAssetType.LANDING_PAGE,
        brief="Modern SaaS landing page for AI startup",
        variations=3,
    )

    assert result["asset_type"] == CreativeAssetType.LANDING_PAGE
    assert len(result["variations"]) == 3
    assert result["status"] == "completed"


@pytest.mark.asyncio
async def test_creative_with_brand_guidelines() -> None:
    """Creative respects brand guidelines."""
    bus = InMemoryEventBus()
    creative = CreativeService(event_bus=bus)

    brand = {
        "primary_color": "#4F46E5",
        "font": "Inter",
        "logo_url": "https://example.com/logo.svg",
    }

    result = await creative.generate(
        asset_type=CreativeAssetType.BANNER,
        brief="Product launch banner",
        brand_guidelines=brand,
    )

    assert result["brand_guidelines"] == brand


@pytest.mark.asyncio
async def test_creative_artifact_retrieval() -> None:
    """Generated artifacts can be retrieved."""
    bus = InMemoryEventBus()
    creative = CreativeService(event_bus=bus)

    result = await creative.generate(
        asset_type=CreativeAssetType.SOCIAL_MEDIA,
        brief="Twitter launch announcement",
    )

    retrieved = await creative.get_artifact(result["artifact_id"])

    assert retrieved is not None
    assert retrieved["artifact_id"] == result["artifact_id"]
