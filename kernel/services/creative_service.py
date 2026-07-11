"""
Creative Service - TASK-14.2

NB2 Lite integration for generating marketing assets, landing pages, presentations.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from kernel.core.event import EventEnvelope
from kernel.core.logging import get_logger
from kernel.core.ports import EventBus


class CreativeAssetType:
    """Supported creative asset types."""

    CAMPAIGN = "campaign"
    LANDING_PAGE = "landing_page"
    BANNER = "banner"
    SOCIAL_MEDIA = "social_media"
    PRESENTATION = "presentation"
    POSTER = "poster"


class CreativeService:
    """
    Creative Service for autonomous asset generation.

    Integrates with NB2 Lite for:
    - Campaign generation
    - Landing page design
    - Banner ads
    - Social media posts
    - Presentations
    - Posters
    """

    def __init__(self, event_bus: EventBus) -> None:
        self._bus = event_bus
        self._logger = get_logger("creative_service")
        self._artifacts: dict[str, Any] = {}

    async def generate(
        self,
        *,
        asset_type: str,
        brief: str,
        brand_guidelines: dict[str, Any] | None = None,
        variations: int = 3,
        mission_id: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate creative assets using NB2 Lite.

        Args:
            asset_type: Type of asset to generate
            brief: Creative brief
            brand_guidelines: Colors, fonts, logos
            variations: Number of variations to generate

        Returns:
            Creative generation result with artifacts
        """
        artifact_id = str(uuid4())

        # Production would call NB2 Lite API
        artifacts = []
        for i in range(variations):
            artifacts.append(
                {
                    "variation_id": f"var-{i+1}",
                    "preview_url": f"https://nb2.example.com/preview/{artifact_id}/v{i+1}",
                    "asset_url": f"https://nb2.example.com/assets/{artifact_id}/v{i+1}",
                    "confidence": 0.8 - (i * 0.05),  # Decreasing confidence for later variations
                }
            )

        result = {
            "artifact_id": artifact_id,
            "asset_type": asset_type,
            "brief": brief,
            "variations": artifacts,
            "brand_guidelines": brand_guidelines or {},
            "status": "completed",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self._artifacts[artifact_id] = result

        # Emit creative event
        event = EventEnvelope.create(
            name="CreativeGenerated",
            payload={
                "artifact_id": artifact_id,
                "asset_type": asset_type,
                "variations_count": len(artifacts),
            },
            mission_id=mission_id,
            trace_id=trace_id,
            confidence=0.8,
            source={"service": "kernel", "module": "creative_service", "component": "generate"},
        )

        await self._bus.publish(event)

        self._logger.info("Creative generated: %s (%d variations)", asset_type, len(artifacts))

        return result

    async def get_artifact(self, artifact_id: str) -> dict[str, Any] | None:
        """Retrieve generated artifact."""
        return self._artifacts.get(artifact_id)

    async def generate_product_launch_campaign(
        self,
        *,
        product_name: str,
        description: str,
        mission_id: str | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate a full social media marketing campaign with copywriting for major platforms
        and Unsplash placeholder image URLs that correspond to product themes.
        """
        artifact_id = str(uuid4())

        keywords = product_name.lower().replace(" ", "-")
        image_url = f"https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=600&q=80"
        if "coffee" in keywords:
            image_url = "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=600&q=80"
        elif "ai" in keywords or "tech" in keywords or "mind" in keywords:
            image_url = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=600&q=80"
        elif "food" in keywords or "delivery" in keywords:
            image_url = "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=80"

        variations = [
            {
                "platform": "X/Twitter",
                "text": f"🚀 Say hello to {product_name}! {description[:80]}... Try it now and revolutionize your workflow! #SaaS #Innovation #{keywords.replace('-', '')}",
                "image_url": image_url,
            },
            {
                "platform": "LinkedIn",
                "text": f"🎯 Introducing {product_name}: {description}\n\nWe're thrilled to announce the launch of our latest innovation designed to deliver maximum value and streamline efficiency. Join us on this journey! #ProductLaunch #Business #TechStartups",
                "image_url": image_url,
            },
            {
                "platform": "Instagram",
                "text": f"✨ Elevate your everyday with {product_name}. Designed beautifully, built intelligently. 👇 Link in bio to learn more! #Aesthetic #Creative #ModernLife #{keywords.replace('-', '')}",
                "image_url": image_url,
            }
        ]

        result = {
            "artifact_id": artifact_id,
            "product_name": product_name,
            "description": description,
            "asset_type": CreativeAssetType.SOCIAL_MEDIA,
            "posts": variations,
            "status": "completed",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self._artifacts[artifact_id] = result

        event = EventEnvelope.create(
            name="CreativeGenerated",
            payload={
                "artifact_id": artifact_id,
                "asset_type": CreativeAssetType.SOCIAL_MEDIA,
                "posts_count": len(variations),
            },
            mission_id=mission_id,
            trace_id=trace_id,
            confidence=0.9,
            source={"service": "kernel", "module": "creative_service", "component": "generate_campaign"},
        )
        await self._bus.publish(event)

        return result
