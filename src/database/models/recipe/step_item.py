from uuid import UUID, uuid4
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base

class StepItem(Base):
    __tablename__ = "step_items"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    step_id: Mapped[UUID] = mapped_column(ForeignKey("recipe_steps.id"), nullable=False)
    item_id: Mapped[UUID] = mapped_column(ForeignKey("items.id"), nullable=False)

    step = relationship("RecipeStep", back_populates="items")
    item = relationship("Item")
