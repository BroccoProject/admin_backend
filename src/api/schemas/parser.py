from pydantic import BaseModel
from api.schemas.recipe_draft import RecipeDraft

class ParseRequest(BaseModel):
    text: str

class ParseResponse(BaseModel):
    thread_id: str
    status: str
    draft: RecipeDraft

class FeedbackRequest(BaseModel):
    feedback: str
