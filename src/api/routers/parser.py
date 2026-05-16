from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.ai.interfaces import IRecipeParserAgent
from api.schemas.parser import ParseRequest, ParseResponse, FeedbackRequest
from services.recipes.parse_recipe import start_recipe_parsing, provide_recipe_feedback
from api.dependencies import get_agent

router = APIRouter(prefix="/parser", tags=["Parser"])

@router.post("", response_model=ParseResponse)
async def start_parsing(
    req: ParseRequest,
    agent: IRecipeParserAgent = Depends(get_agent)
):
    try:
        thread_id, draft = await start_recipe_parsing(agent, req.text)
        return ParseResponse(
            thread_id=thread_id,
            status="awaiting_review",
            draft=draft
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")

@router.post("/{thread_id}", response_model=ParseResponse)
async def provide_feedback(
    thread_id: str,
    req: FeedbackRequest,
    agent: IRecipeParserAgent = Depends(get_agent)
):
    try:
        draft = await provide_recipe_feedback(agent, thread_id, req.feedback)
        return ParseResponse(
            thread_id=thread_id,
            status="awaiting_review",
            draft=draft
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")
