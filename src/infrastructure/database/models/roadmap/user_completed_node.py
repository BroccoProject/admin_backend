from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Text, text
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.connection import Base


class UserCompletedNode(Base):
    __tablename__ = "user_completed_nodes"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True
    )
    node_id: Mapped[UUID] = mapped_column(
        ForeignKey("roadmap_nodes.id", ondelete="CASCADE"), primary_key=True
    )
    stars_earned: Mapped[int | None] = mapped_column(Integer, server_default="1")
    completed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("timezone('utc', now())"),
    )
    image_url: Mapped[str | None] = mapped_column(Text)
