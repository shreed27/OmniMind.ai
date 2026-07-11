from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any
from kernel.services.git_history_service import GitHistoryService

router = APIRouter(prefix="/api/v1/git", tags=["git"])
git_service = GitHistoryService()


class DiffRequest(BaseModel):
    diff: str | None = None


@router.post("/history")
async def generate_history(request: DiffRequest) -> dict[str, Any]:
    diff = request.diff
    if diff is None:
        diff = git_service.get_local_diff()
    
    commit_msg = await git_service.generate_commit_message(diff)
    pr_desc = await git_service.generate_pr_description(diff)
    
    return {
        "commit_message": commit_msg,
        "pr_description": pr_desc,
        "diff_length": len(diff),
    }
