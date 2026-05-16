from uuid import UUID, uuid4
from sqlalchemy import Text, text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.database.connection import Base
from infrastructure.database.models.enums import ItemTag

class Item(Base):
    __tablename__ = "items"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, server_default=text("gen_random_uuid()"))
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name_i18n: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"), nullable=False)
    tag: Mapped[ItemTag] = mapped_column(SQLEnum(ItemTag, name="item_tag_enum"), nullable=False)
