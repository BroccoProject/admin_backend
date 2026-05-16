from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, text
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.connection import Base


class UserUnlockedCategory(Base):
    __tablename__ = "user_unlocked_categories"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True
    )
    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True
    )
    unlocked_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("timezone('utc', now())"),
    )
    completed_nodes_count: Mapped[int | None] = mapped_column(Integer, server_default="0")
