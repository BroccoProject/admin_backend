import datetime
from uuid import UUID, uuid4
from sqlalchemy import Text, DateTime, text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.database.connection import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, server_default=text("gen_random_uuid()"))
    thread_id: Mapped[str] = mapped_column(Text, index=True, nullable=False)
    message: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=text("now()"), 
        nullable=False
    )
