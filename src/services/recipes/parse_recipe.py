import uuid
from infrastructure.ai.interfaces import IRecipeParserAgent
from api.schemas.recipe_draft import RecipeDraft as ApiRecipeDraft

async def start_recipe_parsing(agent: IRecipeParserAgent, text: str) -> tuple[str, ApiRecipeDraft]:
    """Starts a new LangChain parsing session for a given raw recipe text."""
    thread_id = str(uuid.uuid4())
    infra_draft = await agent.parse_recipe(text, thread_id)
    api_draft = ApiRecipeDraft.model_validate(infra_draft.model_dump())
    return thread_id, api_draft

async def provide_recipe_feedback(agent: IRecipeParserAgent, thread_id: str, feedback: str) -> ApiRecipeDraft:
    """Applies user feedback to an existing parsing session to correct the output."""
    infra_draft = await agent.parse_recipe(f"User feedback/correction: {feedback}", thread_id)
    api_draft = ApiRecipeDraft.model_validate(infra_draft.model_dump())
    return api_draft
