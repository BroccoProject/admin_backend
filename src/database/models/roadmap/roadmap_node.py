from uuid import UUID, uuid4
from sqlalchemy import Text, Integer, ForeignKey, ARRAY, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base

class RoadmapNode(Base):
    __tablename__ = "roadmap_nodes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, server_default=text("gen_random_uuid()"))
    category_id: Mapped[UUID | None] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    recipe_id: Mapped[UUID | None] = mapped_column(ForeignKey("recipes.id", ondelete="RESTRICT"))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    preview_image_url: Mapped[str | None] = mapped_column(Text)
    map_column: Mapped[int] = mapped_column(Integer, nullable=False)
    map_row: Mapped[int] = mapped_column(Integer, nullable=False)
    prerequisite_ids: Mapped[list[UUID] | None] = mapped_column(ARRAY(PG_UUID), server_default=text("'{}'::uuid[]"))

    category = relationship("Category", back_populates="nodes")
    recipe = relationship("Recipe")
