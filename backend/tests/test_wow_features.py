from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_ai_git_history_endpoint() -> None:
    # Test generating commit/PR description from a mock diff
    mock_diff = """diff --git a/backend/app/main.py b/backend/app/main.py
index 12345..67890 100644
--- a/backend/app/main.py
+++ b/backend/app/main.py
@@ -10,3 +10,4 @@
+print("wow features added")
"""
    response = client.post("/api/v1/git/history", json={"diff": mock_diff})
    assert response.status_code == 200
    data = response.json()
    assert "commit_message" in data
    assert "pr_description" in data
    assert "main" in data["commit_message"]


def test_creative_campaign_endpoint() -> None:
    # Test generating social media campaign copywriting and product mockups
    payload = {
        "product_name": "AI Coffee Brewer",
        "description": "An intelligent coffee machine that monitors your focus levels and brews a tailored espresso."
    }
    response = client.post("/api/v1/creative/product-campaign", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["product_name"] == "AI Coffee Brewer"
    assert len(data["posts"]) == 3
    
    platforms = [post["platform"] for post in data["posts"]]
    assert "X/Twitter" in platforms
    assert "LinkedIn" in platforms
    assert "Instagram" in platforms
    
    assert "unsplash" in data["posts"][0]["image_url"]
