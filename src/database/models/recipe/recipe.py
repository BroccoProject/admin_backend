from uuid import UUID, uuid4
from sqlalchemy import Text, Integer, JSON, ARRAY, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base
from database.models.enums import DifficultyLevel

class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    title_i18n: Mapped[dict] = mapped_column(JSON, default={}, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    description_i18n: Mapped[dict] = mapped_column(JSON, default={}, nullable=False)
    image_url: Mapped[str | None] = mapped_column(Text)
    difficulty_level: Mapped[DifficultyLevel | None] = mapped_column(SQLEnum(DifficultyLevel))
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    youtube_url: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), default=[])
    category: Mapped[str | None] = mapped_column(Text)
    area: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(Text)

    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    steps = relationship("RecipeStep", back_populates="recipe", cascade="all, delete-orphan")
