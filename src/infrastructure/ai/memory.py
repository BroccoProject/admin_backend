import json
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, messages_from_dict, message_to_dict

from infrastructure.database.models.core.chat_history import ChatHistory


class AsyncSQLAlchemyChatMessageHistory(BaseChatMessageHistory):
    """
    Async implementation of LangChain's BaseChatMessageHistory using
    the existing SQLAlchemy AsyncSession and Postgres JSONB column.
    """

    def __init__(self, session_id: str, db: AsyncSession):
        self.session_id = session_id
        self.db = db

    async def aget_messages(self) -> list[BaseMessage]:
        result = await self.db.execute(
            select(ChatHistory)
            .where(ChatHistory.thread_id == self.session_id)
            .order_by(ChatHistory.created_at.asc())
        )
        records = result.scalars().all()
        return messages_from_dict([record.message for record in records])

    async def aadd_messages(self, messages: Sequence[BaseMessage]) -> None:
        for message in messages:
            chat_msg = ChatHistory(
                thread_id=self.session_id,
                message=message_to_dict(message)
            )
            self.db.add(chat_msg)
        await self.db.commit()

    async def aclear(self) -> None:
        pass

    @property
    def messages(self) -> list[BaseMessage]:
        raise NotImplementedError("Synchronous access is not supported. Use aget_messages().")

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        raise NotImplementedError("Synchronous access is not supported. Use aadd_messages().")

    def clear(self) -> None:
        raise NotImplementedError("Synchronous access is not supported. Use aclear().")
