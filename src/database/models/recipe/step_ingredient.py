from uuid import UUID, uuid4
from sqlalchemy import Text, Numeric, ForeignKey, ARRAY, Enum as SQLEnum, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base
from database.models.enums import IngredientAction

class StepIngredient(Base):
    __tablename__ = "step_ingredients"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, server_default=text("gen_random_uuid()"))
    step_id: Mapped[UUID] = mapped_column(ForeignKey("recipe_steps.id", ondelete="CASCADE"), nullable=False)
    ingredient_id: Mapped[UUID] = mapped_column(ForeignKey("ingredients.id"), nullable=False)
    amount: Mapped[float | None] = mapped_column(Numeric)
    unit: Mapped[str | None] = mapped_column(Text)
    actions: Mapped[list[IngredientAction] | None] = mapped_column(ARRAY(SQLEnum(IngredientAction, name="ingredient_action_enum")), server_default=text("'{}'::ingredient_action_enum[]"))

    __table_args__ = (
        UniqueConstraint("step_id", "ingredient_id", name="step_ingredients_unique"),
    )

    step = relationship("RecipeStep", back_populates="ingredients")
    ingredient = relationship("Ingredient")
