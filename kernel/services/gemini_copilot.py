from __future__ import annotations

import httpx
import json
import os
from typing import Any


class GeminiCopilotService:
    """
    Google Gemini API Integration Copilot.
    Unlocks live, dynamic corporate board debates and platform copywriting
    using Gemini 1.5 Flash.
    """

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY", "")

    def is_active(self) -> bool:
        return bool(self.api_key)

    async def generate_debate(self, objective: str) -> dict[str, Any]:
        """
        Dynamically simulate a boardroom debate between CEO, CTO, and CFO
        regarding the user's objective using Gemini.
        """
        if not self.is_active():
            return {
                "dynamic": False,
                "conflict": {
                    "type": "budget_exceeded",
                    "raised_by": "CTO",
                    "description": "Proposed deployment budget ($12,500) exceeds maximum automated limit ($10,000)."
                },
                "debate_transcript": [
                    {
                        "speaker": "CEO",
                        "role": "Chief Executive Officer",
                        "argument": f"Let's figure out how to build and market '{objective}'. CTO, what is our technical approach?",
                        "evidence_ref": "objective-analysis"
                    },
                    {
                        "speaker": "CTO",
                        "role": "Chief Technology Officer",
                        "argument": "The engineering stack is feasible, but we need high-performance Frontier nodes. Cost estimate is $12,500.",
                        "evidence_ref": "node-calibration-v2"
                    },
                    {
                        "speaker": "CFO",
                        "role": "Chief Financial Officer",
                        "argument": "That exceeds our normal limit. CFO is issuing a threshold exception approval, liquid balance is sufficient.",
                        "evidence_ref": "cost-ledger-q2"
                    }
                ],
                "votes": [
                    {"voter": "CTO", "stance": "YES", "confidence": 0.95, "reason": "Requires optimal calibrations"},
                    {"voter": "CFO", "stance": "YES", "confidence": 0.75, "reason": "Exception authorized by finance"},
                    {"voter": "COO", "stance": "YES", "confidence": 0.8, "reason": "Aligned with timeline"},
                    {"voter": "CMO", "stance": "YES", "confidence": 0.7, "reason": "Ensures polished outward asset delivery"}
                ],
                "outcome": "PASSED"
            }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        
        prompt = f"""
        You are roleplaying as the Executive Board of a highly advanced AI-first autonomous enterprise.
        The user has given the following business objective: "{objective}".
        
        Generate a structured JSON response containing:
        1. A "conflict": A potential operational conflict (e.g., budget limits, tech stacks, or delivery timeframes) raised by the CTO or CFO.
        2. A "debate_transcript": A conversation of 3 turns where:
           - CTO (Chief Technology Officer) argues from a technical and quality perspective.
           - CFO (Chief Financial Officer) argues from a cost and risk mitigation perspective.
           - CEO (Chief Executive Officer) facilitates and seeks consensus.
        3. A "votes": An array of vote objects representing the stance (YES or NO), confidence (float between 0 and 1), and a precise reason for CTO, CFO, COO, and CMO.
        4. An "outcome": Either "PASSED" or "REJECTED" based on majority voting.

        Return ONLY raw JSON matching this schema:
        {{
            "conflict": {{ "type": "string", "raised_by": "string", "description": "string" }},
            "debate_transcript": [
                {{ "speaker": "CEO|CTO|CFO", "role": "string", "argument": "string", "evidence_ref": "string" }}
            ],
            "votes": [
                {{ "voter": "CTO|CFO|COO|CMO", "stance": "YES|NO", "confidence": 0.9, "reason": "string" }}
            ],
            "outcome": "PASSED|REJECTED"
        }}
        """

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "responseMimeType": "application/json"
                        }
                    },
                    timeout=15.0
                )
                if response.status_code == 200:
                    data = response.json()
                    text_response = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(text_response)
                    parsed["dynamic"] = True
                    return parsed
        except Exception:
            pass
            
        return {
            "dynamic": False,
            "conflict": {
                "type": "budget_exceeded",
                "raised_by": "CTO",
                "description": "Proposed deployment budget ($12,500) exceeds maximum automated limit ($10,000)."
            },
            "debate_transcript": [
                {"speaker": "CEO", "role": "Chief Executive Officer", "argument": f"Let's figure out how to build and market '{objective}'."}
            ],
            "votes": [],
            "outcome": "PASSED"
        }

    async def generate_marketing_copy(self, product_name: str, description: str) -> dict[str, Any]:
        """
        Use Gemini to write highly engaging, custom social media posts for Twitter, LinkedIn, and Instagram.
        """
        if not self.is_active():
            return {}

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        prompt = f"""
        You are a elite copywriting and growth marketing agent.
        Write highly engaging social media posts for the product launch of "{product_name}".
        Product Description: "{description}"
        
        Generate a structured JSON response containing copywriting for:
        1. "X/Twitter" (Short, catchy, high-impact, hashtags, and a hook, maximum 280 chars).
        2. "LinkedIn" (Professional, value-oriented, thought-leadership, structured with bullet points, calls-to-action).
        3. "Instagram" (Aesthetic, trend-oriented, engaging emojis, bio link call-to-action).

        Return ONLY raw JSON matching this schema:
        {{
            "Twitter": "string",
            "LinkedIn": "string",
            "Instagram": "string"
        }}
        """

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "responseMimeType": "application/json"
                        }
                    },
                    timeout=15.0
                )
                if response.status_code == 200:
                    data = response.json()
                    text_response = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(text_response)
                    return parsed
        except Exception:
            pass
        return {}
