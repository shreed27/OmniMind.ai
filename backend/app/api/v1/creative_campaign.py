from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any
from kernel.services.creative_service import CreativeService
from kernel.core.event import EventBus
from kernel.services.gemini_copilot import GeminiCopilotService

router = APIRouter(prefix="/api/v1/creative", tags=["creative"])
event_bus = EventBus()
creative_service = CreativeService(event_bus=event_bus)
gemini_service = GeminiCopilotService()


class CampaignRequest(BaseModel):
    product_name: str
    description: str


@router.post("/product-campaign")
async def generate_campaign(request: CampaignRequest) -> dict[str, Any]:
    if not request.product_name or not request.description:
        raise HTTPException(status_code=422, detail="Missing product name or description")
    
    # 1. Base Unsplash image-guided creative generation
    result = await creative_service.generate_product_launch_campaign(
        product_name=request.product_name,
        description=request.description,
    )
    
    # 2. If Gemini is active, override with dynamic high-fidelity copywriting!
    if gemini_service.is_active():
        gemini_posts = await gemini_service.generate_marketing_copy(
            product_name=request.product_name,
            description=request.description,
        )
        if gemini_posts:
            # map gemini response keys to result posts
            for post in result["posts"]:
                platform = post["platform"]
                if platform == "X/Twitter" and "Twitter" in gemini_posts:
                    post["text"] = gemini_posts["Twitter"]
                elif platform == "LinkedIn" and "LinkedIn" in gemini_posts:
                    post["text"] = gemini_posts["LinkedIn"]
                elif platform == "Instagram" and "Instagram" in gemini_posts:
                    post["text"] = gemini_posts["Instagram"]
            result["dynamic_gemini_copywriting"] = True

    return result
