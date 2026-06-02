from uuid import UUID, uuid4
from sqlalchemy import Text, Integer, text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from infrastructure.database.connection import Base

class RecipeStep(Base):
    __tablename__ = "recipe_steps"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, server_default=text("gen_random_uuid()"))
    recipe_id: Mapped[UUID] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    instruction: Mapped[str] = mapped_column(Text, nullable=False)
    instruction_i18n: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"), nullable=False)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)

    __table_args__ = (
        UniqueConstraint("recipe_id", "step_number", name="recipe_steps_unique"),
    )

    recipe = relationship("Recipe", back_populates="steps")
    ingredients = relationship("StepIngredient", back_populates="step", cascade="all, delete-orphan")
    items = relationship("StepItem", back_populates="step", cascade="all, delete-orphan")
