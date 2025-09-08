# src/api/shiksha_api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.agents.shiksha.new_shiksha_orchestrator import ShikshaOrchestrator

router = APIRouter()
orch = ShikshaOrchestrator()

class CreateCourseRequest(BaseModel):
    topic: str
    chapters: Optional[int] = 5
    audience: Optional[str] = "beginners"
    push: Optional[bool] = False
    sheet_id: Optional[str] = None

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/create-course")
async def create_course(req: CreateCourseRequest):
    try:
        out = orch.generate_course(req.topic, chapters=req.chapters, audience=req.audience)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")

    result = {
        "ok": True,
        "json_path": out["json_path"],
        "out_dir": out["out_dir"],
        "course_title": out["course"].get("title")
    }

    if req.push:
        if not req.sheet_id:
            raise HTTPException(status_code=400, detail="sheet_id is required when push=true")
        try:
            push_res = orch.push_to_database(out["json_path"], req.sheet_id)
            result["push"] = push_res
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Push to database failed: {e}")

    return result

