"""initial admin tables

Revision ID: aa362f860586
Revises: 
Create Date: 2026-05-24 14:04:48.215755

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'aa362f860586'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('admin_profiles',
    sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('role', sa.Enum('editor', 'admin', name='admin_role'), server_default='editor', nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['admin_profiles.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['auth.users.id'], ondelete='CASCADE', use_alter=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('access_requests',
    sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='access_request_status'), server_default='pending', nullable=False),
    sa.Column('token', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('token_used', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('token_expires_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now() + interval '48 hours'"), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('resolved_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('resolved_by', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['resolved_by'], ['admin_profiles.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['auth.users.id'], ondelete='CASCADE', use_alter=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    op.create_index('ix_access_requests_user_id_pending', 'access_requests', ['user_id'], unique=True, postgresql_where=sa.text("status = 'pending'"))


def downgrade() -> None:
    op.drop_index('ix_access_requests_user_id_pending', table_name='access_requests', postgresql_where=sa.text("status = 'pending'"))
    op.drop_table('access_requests')
    op.drop_table('admin_profiles')
    op.execute("DROP TYPE IF EXISTS admin_role")
    op.execute("DROP TYPE IF EXISTS access_request_status")
