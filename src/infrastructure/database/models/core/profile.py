from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Text, Integer, Date, TIMESTAMP, text, REAL, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.connection import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    username: Mapped[str | None] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    cooking_skill: Mapped[str | None] = mapped_column(Text)
    max_cooking_time_minutes: Mapped[int | None] = mapped_column(Integer)
    usage_frequency: Mapped[str | None] = mapped_column(Text)
    eating_style: Mapped[str | None] = mapped_column(Text)
    main_goal: Mapped[str | None] = mapped_column(Text)
    gender: Mapped[str | None] = mapped_column(Text)
    birth_date: Mapped[date | None] = mapped_column(Date)
    height_cm: Mapped[int | None] = mapped_column(Integer)
    current_weight_kg: Mapped[float | None] = mapped_column(REAL)
    target_weight_kg: Mapped[float | None] = mapped_column(REAL)
    activity_level: Mapped[str | None] = mapped_column(Text)
    stars_bank: Mapped[int | None] = mapped_column(Integer, server_default="0")
    total_xp: Mapped[int | None] = mapped_column(Integer, server_default="0")
    current_streak: Mapped[int | None] = mapped_column(Integer, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("timezone('utc', now())"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("timezone('utc', now())"),
        onupdate=text("timezone('utc', now())"),
    )
