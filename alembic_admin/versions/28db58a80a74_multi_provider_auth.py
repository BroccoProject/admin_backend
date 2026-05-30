"""multi_provider_auth

Revision ID: 28db58a80a74
Revises: ebcf3a6d4d4f
Create Date: 2026-05-30 21:54:23.471950

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28db58a80a74'
down_revision: Union[str, Sequence[str], None] = 'ebcf3a6d4d4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    # Drop tables to recreate them
    op.drop_table('access_requests')
    op.drop_table('admin_profiles')

    # Drop existing enums to avoid conflicts when recreating
    op.execute("DROP TYPE IF EXISTS access_request_status")
    op.execute("DROP TYPE IF EXISTS admin_role")

    # Create admin_profiles
    op.create_table('admin_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('auth_provider', sa.String(), nullable=False),
        sa.Column('provider_id', sa.String(), nullable=True),
        sa.Column('password_hash', sa.String(), nullable=True),
        sa.Column('role', sa.Enum('editor', 'admin', 'viewer', name='admin_role'), server_default='editor', nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint("auth_provider IN ('google', 'github', 'local')", name='check_auth_provider'),
        sa.ForeignKeyConstraint(['created_by'], ['admin_profiles.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_admin_profiles_provider_id', 'admin_profiles', ['provider_id'], unique=True, postgresql_where=sa.text('provider_id IS NOT NULL'))

    # Create access_requests
    op.create_table('access_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='access_request_status'), server_default='pending', nullable=False),
        sa.Column('token', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('token_used', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('token_expires_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now() + interval '48 hours'"), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('resolved_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['resolved_by'], ['admin_profiles.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    op.create_index('ix_access_requests_email_pending', 'access_requests', ['email'], unique=True, postgresql_where=sa.text("status = 'pending'"))

def downgrade() -> None:
    pass
