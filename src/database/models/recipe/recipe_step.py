from uuid import UUID, uuid4
from sqlalchemy import Text, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base

class RecipeStep(Base):
    __tablename__ = "recipe_steps"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    recipe_id: Mapped[UUID] = mapped_column(ForeignKey("recipes.id"), nullable=False)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    instruction: Mapped[str] = mapped_column(Text, nullable=False)
    instruction_i18n: Mapped[dict] = mapped_column(JSON, default={}, nullable=False)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)

    recipe = relationship("Recipe", back_populates="steps")
    ingredients = relationship("StepIngredient", back_populates="step", cascade="all, delete-orphan")
    items = relationship("StepItem", back_populates="step", cascade="all, delete-orphan")
