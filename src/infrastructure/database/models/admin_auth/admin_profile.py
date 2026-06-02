from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import String, text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, TIMESTAMP
from sqlalchemy import Index, CheckConstraint, UniqueConstraint

from infrastructure.database.connection_admin import AdminBase

class AdminProfile(AdminBase):
    __tablename__ = "admin_profiles"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, server_default=text("gen_random_uuid()")
    )
    email: Mapped[str] = mapped_column(String, nullable=False)
    auth_provider: Mapped[str] = mapped_column(String, nullable=False)
    provider_id: Mapped[str | None] = mapped_column(String, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(
        SAEnum('editor', 'admin', 'viewer', name='admin_role'),
        nullable=False,
        server_default='editor'
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    created_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("admin_profiles.id", ondelete="SET NULL"),
        nullable=True
    )

    __table_args__ = (
        CheckConstraint(auth_provider.in_(['google', 'github', 'local']), name='check_auth_provider'),
        Index('ix_admin_profiles_provider_id', provider_id, unique=True, postgresql_where=provider_id.isnot(None)),
        UniqueConstraint('email', 'auth_provider', name='uq_admin_profiles_email_provider'),
    )