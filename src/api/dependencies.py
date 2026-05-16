from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.connection import AsyncSessionLocal
from infrastructure.ai.interfaces import IRecipeParserAgent
from infrastructure.ai.agent import get_parser_agent

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_agent(db: AsyncSession = Depends(get_db)) -> IRecipeParserAgent:
    """Dependency injection for the recipe parser agent."""
    return get_parser_agent(db)
