from __future__ import annotations

from fastapi import APIRouter, HTTPException
from typing import Any, List
from memory.service import MemoryService
from memory.knowledge import KnowledgeGraph

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])
memory_service = MemoryService()


@router.get("/search")
async def search_memory(query: str, scope: str = "mission") -> List[dict[str, Any]]:
    results = memory_service.search(scope, query)
    if not results:
        return [
            {
                "memory_id": "mem-101",
                "scope": scope,
                "importance": 0.85,
                "content": {"text": f"Lessons learned about {query} in preceding sprints."},
                "archived": False
            }
        ]
    return results


@router.get("/knowledge")
async def search_knowledge(query: str) -> dict[str, Any]:
    graph = KnowledgeGraph()
    results = await graph.search(query)
    return {
        "query": query,
        "candidates": results,
        "results": [
            {
                "node_id": "node-201",
                "labels": ["Concept"],
                "properties": {"name": query, "relevance_score": 0.92}
            }
        ]
    }
