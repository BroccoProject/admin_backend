from uuid import UUID, uuid4
from sqlalchemy import Text, Integer, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from infrastructure.database.connection import Base

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, server_default=text("gen_random_uuid()"))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    subtitle: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text)
    unlock_cost_stars: Mapped[int | None] = mapped_column(Integer, server_default="0")
    category_area: Mapped[str | None] = mapped_column(Text)
    category_type: Mapped[str | None] = mapped_column(Text)
    total_nodes: Mapped[int | None] = mapped_column(Integer, server_default="0")

    nodes = relationship("RoadmapNode", back_populates="category", cascade="all, delete-orphan")
