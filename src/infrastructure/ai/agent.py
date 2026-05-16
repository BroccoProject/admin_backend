import logging
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables.history import RunnableWithMessageHistory

from core.config import settings
from infrastructure.ai.schemas import RecipeDraft
from infrastructure.ai.prompts import PARSE_PROMPT
from infrastructure.ai.memory import AsyncSQLAlchemyChatMessageHistory
from infrastructure.ai.interfaces import IRecipeParserAgent

logger = logging.getLogger(__name__)

class LangChainRecipeParserAgent(IRecipeParserAgent):
    def __init__(self, db: AsyncSession):
        self.db = db
        
        llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            temperature=0,
            api_key=settings.GOOGLE_API_KEY,
        ).with_structured_output(RecipeDraft)

        chain = PARSE_PROMPT | llm

        def get_session_history(session_id: str):
            return AsyncSQLAlchemyChatMessageHistory(session_id, self.db)

        self.agent = RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    async def parse_recipe(self, input_text: str, thread_id: str) -> RecipeDraft:
        draft = await self.agent.ainvoke(
            {"input": input_text},
            config={"configurable": {"session_id": thread_id}}
        )
        return draft

def get_parser_agent(db: AsyncSession) -> IRecipeParserAgent:
    """Factory method to get an instance of the parser agent."""
    return LangChainRecipeParserAgent(db)
