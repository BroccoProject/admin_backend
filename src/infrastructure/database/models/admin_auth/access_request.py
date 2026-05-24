from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import String, Text, Boolean, text, ForeignKey, Enum as SAEnum, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import TIMESTAMP

from infrastructure.database.connection_admin import AdminBase

class AccessRequest(AdminBase):
    __tablename__ = "access_requests"
    __table_args__ = (
        Index(
            "ix_access_requests_google_sub_pending",
            "google_sub",
            unique=True,
            postgresql_where=text("status = 'pending'")
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, server_default=text("gen_random_uuid()")
    )
    google_sub: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum('pending', 'approved', 'rejected', name='access_request_status'),
        nullable=False,
        server_default='pending'
    )
    token: Mapped[UUID] = mapped_column(
        nullable=False,
        unique=True,
        default=uuid4,
        server_default=text("gen_random_uuid()")
    )
    token_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    token_expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now() + interval '48 hours'")
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    resolved_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("admin_profiles.id", ondelete="SET NULL"),
        nullable=True
    )
