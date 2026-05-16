from uuid import UUID, uuid4
from sqlalchemy import Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from database.connection import Base

class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name_i18n: Mapped[dict] = mapped_column(JSON, default={}, nullable=False)
    default_unit: Mapped[str | None] = mapped_column(Text)
