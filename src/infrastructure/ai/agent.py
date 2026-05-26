import logging
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables.history import RunnableWithMessageHistory

from core.config import settings
from infrastructure.ai.schemas import RecipeBodyDraft, RecipeDraft, RecipeMetaDraft
from infrastructure.ai.prompts import META_PROMPT, PARSE_PROMPT
from infrastructure.ai.memory import AsyncSQLAlchemyChatMessageHistory
from infrastructure.ai.interfaces import IRecipeParserAgent

logger = logging.getLogger(__name__)


class LangChainRecipeParserAgent(IRecipeParserAgent):
    def __init__(self, db: AsyncSession):
        self.db = db

        base_llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            temperature=0,
            api_key=settings.GOOGLE_API_KEY,
        )

        meta_llm = base_llm.with_structured_output(RecipeMetaDraft)
        meta_chain = META_PROMPT | meta_llm

        body_llm = base_llm.with_structured_output(RecipeBodyDraft)
        body_chain = PARSE_PROMPT | body_llm

        def get_session_history(session_id: str):
            return AsyncSQLAlchemyChatMessageHistory(session_id, self.db)

        self._meta_agent = RunnableWithMessageHistory(
            meta_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

        self._body_agent = RunnableWithMessageHistory(
            body_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    async def parse_recipe(self, input_text: str, thread_id: str) -> RecipeDraft:
        config = {"configurable": {"session_id": thread_id}}

        logger.info("[%s] Step 1: extracting recipe metadata…", thread_id)
        meta: RecipeMetaDraft = await self._meta_agent.ainvoke(
            {"input": input_text}, config=config
        )
        logger.info(
            "[%s] Step 1 done — title=%r, category=%r, difficulty=%r, tags=%s",
            thread_id, meta.title, meta.category, meta.difficulty, meta.tags,
        )

        logger.info("[%s] Step 2: extracting steps and ingredients…", thread_id)
        body: RecipeBodyDraft = await self._body_agent.ainvoke(
            {"input": input_text}, config=config
        )
        logger.info(
            "[%s] Step 2 done — %d ingredient(s), %d step(s)",
            thread_id, len(body.ingredients), len(body.steps),
        )

        draft = RecipeDraft.from_steps(meta, body)
        logger.info("[%s] Recipe draft assembled successfully.", thread_id)
        return draft


def get_parser_agent(db: AsyncSession) -> IRecipeParserAgent:
    return LangChainRecipeParserAgent(db)
