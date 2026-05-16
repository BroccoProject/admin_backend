from uuid import UUID, uuid4
from sqlalchemy import Text, Numeric, Integer, ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from infrastructure.database.connection import Base

class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, server_default=text("gen_random_uuid()"))
    recipe_id: Mapped[UUID] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    ingredient_id: Mapped[UUID] = mapped_column(ForeignKey("ingredients.id"), nullable=False)
    amount: Mapped[float | None] = mapped_column(Numeric)
    unit: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)

    __table_args__ = (
        UniqueConstraint("recipe_id", "ingredient_id", name="recipe_ingredients_unique"),
    )

    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient")
