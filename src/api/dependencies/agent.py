from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies.db import get_db
from infrastructure.ai.interfaces import IRecipeParserAgent
from infrastructure.ai.agent import get_parser_agent

def get_agent(db: AsyncSession = Depends(get_db)) -> IRecipeParserAgent:
    """Dependency injection for the recipe parser agent."""
    return get_parser_agent(db)
