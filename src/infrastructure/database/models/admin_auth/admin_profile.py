from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import String, text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, TIMESTAMP

from infrastructure.database.connection import Base

class AdminProfile(Base):
    __tablename__ = "admin_profiles"
    __table_args__ = {"schema": "admin_auth"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("auth.users.id", ondelete="CASCADE", use_alter=True),
        nullable=False,
        unique=True
    )
    email: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(
        SAEnum('editor', 'admin', name='admin_role', schema='admin_auth'),
        nullable=False,
        server_default='editor'
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    created_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("admin_auth.admin_profiles.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships (Optional, but good for ORM navigation)
    # creator = relationship("AdminProfile", remote_side=[id])
