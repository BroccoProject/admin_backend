from uuid import UUID, uuid4
from sqlalchemy import Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from database.connection import Base
from database.models.enums import ItemTag

class Item(Base):
    __tablename__ = "items"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name_i18n: Mapped[dict] = mapped_column(JSON, default={}, nullable=False)
    tag: Mapped[ItemTag] = mapped_column(SQLEnum(ItemTag), nullable=False)
