"""API routes for Shiksha course orchestration."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from ..agents.shiksha.shiksha_orchestrator import ShikshaOrchestrator
from ..agents.shiksha.enhanced_shiksha_orchestrator import EnhancedShikshaOrchestrator

router = APIRouter(prefix="/shiksha", tags=["Shiksha"])
logger = logging.getLogger("ShikshaAPI")


class CourseRequest(BaseModel):
    name: str
    description: str
    difficulty: Optional[str] = "Beginner"
    roadmap: Optional[str] = "General"
    enhanced: Optional[bool] = False


@router.post("/create")
async def create_course(req: CourseRequest) -> Dict[str, Any]:
    """Create a course (basic or enhanced)."""
    try:
        if req.enhanced:
            orchestrator = EnhancedShikshaOrchestrator()
            course = orchestrator.create_world_class_course(
                req.name, req.description, req.difficulty, req.roadmap
            )
        else:
            orchestrator = ShikshaOrchestrator()
            course = orchestrator.create_complete_course(
                req.name, req.description, req.difficulty, req.roadmap
            )

        return {"status": True, "course": course}

    except Exception as e:
        logger.error(f"Error creating course: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check for Shiksha routes."""
    return {"status": True, "message": "Shiksha API is running"}
