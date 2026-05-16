from uuid import UUID, uuid4
from sqlalchemy import ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base

class StepItem(Base):
    __tablename__ = "step_items"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, server_default=text("gen_random_uuid()"))
    step_id: Mapped[UUID] = mapped_column(ForeignKey("recipe_steps.id", ondelete="CASCADE"), nullable=False)
    item_id: Mapped[UUID] = mapped_column(ForeignKey("items.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("step_id", "item_id", name="step_items_unique"),
    )

    step = relationship("RecipeStep", back_populates="items")
    item = relationship("Item")
