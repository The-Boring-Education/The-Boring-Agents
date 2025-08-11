from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from ..agents.interview.interview_sheet_manager import InterviewSheetManager
from ..agents.interview.types import AnswerAgentType


class GenerateInterviewSheetRequest(BaseModel):
    mdx_file: str = Field(..., description="Path to MDX requirements or questions file")
    agent_type: AnswerAgentType = Field(default=AnswerAgentType.GENERIC)
    technology: Optional[str] = Field(default=None)
    save: bool = Field(default=True)


class InterviewSheetResponse(BaseModel):
    ok: bool
    message: str
    output_file: Optional[str] = None
    sheet: Optional[dict] = None


router = APIRouter(prefix="/interview", tags=["interview"])


@router.post("/create-sheet", response_model=InterviewSheetResponse)
def create_sheet(payload: GenerateInterviewSheetRequest):
    manager = InterviewSheetManager(agent_type=payload.agent_type)
    try:
        result = manager.create_sheet_from_mdx(mdx_filepath=payload.mdx_file)
    except Exception as e:  # surface failure clearly to API clients
        raise HTTPException(status_code=400, detail=str(e))

    output_file = result.get("output_file") if payload.save else None
    return InterviewSheetResponse(
        ok=True,
        message="Interview sheet created",
        output_file=output_file,
        sheet=result.get("sheet"),
    )

