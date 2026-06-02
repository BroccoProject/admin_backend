"""Add cascade deletes to foreign keys

Revision ID: 02e32a65ded4
Revises: d1d0514d1366
Create Date: 2026-05-16 19:20:24.609258

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '02e32a65ded4'
down_revision: Union[str, Sequence[str], None] = 'd1d0514d1366'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Clean recipe ingredients cascade on recipe delete
    op.drop_constraint('recipe_ingredients_recipe_id_fkey', 'recipe_ingredients', type_='foreignkey')
    op.create_foreign_key('recipe_ingredients_recipe_id_fkey', 'recipe_ingredients', 'recipes', ['recipe_id'], ['id'], ondelete='CASCADE')

    # 2. Clean recipe steps cascade on recipe delete
    op.drop_constraint('recipe_steps_recipe_id_fkey', 'recipe_steps', type_='foreignkey')
    op.create_foreign_key('recipe_steps_recipe_id_fkey', 'recipe_steps', 'recipes', ['recipe_id'], ['id'], ondelete='CASCADE')

    # 3. Clean sub-step ingredients cascade on step delete
    op.drop_constraint('step_ingredients_step_id_fkey', 'step_ingredients', type_='foreignkey')
    op.create_foreign_key('step_ingredients_step_id_fkey', 'step_ingredients', 'recipe_steps', ['step_id'], ['id'], ondelete='CASCADE')

    # 4. Clean sub-step items cascade on step delete
    op.drop_constraint('step_items_step_id_fkey', 'step_items', type_='foreignkey')
    op.create_foreign_key('step_items_step_id_fkey', 'step_items', 'recipe_steps', ['step_id'], ['id'], ondelete='CASCADE')

    # 5. Clean roadmap nodes cascade on category delete (Blocked automatically if a user unlocked it or finished it)
    op.drop_constraint('roadmap_nodes_category_id_fkey', 'roadmap_nodes', type_='foreignkey')
    op.create_foreign_key('roadmap_nodes_category_id_fkey', 'roadmap_nodes', 'categories', ['category_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    # Reverts everything safely back to strict, manual-cleanup constraints
    op.drop_constraint('roadmap_nodes_category_id_fkey', 'roadmap_nodes', type_='foreignkey')
    op.create_foreign_key('roadmap_nodes_category_id_fkey', 'roadmap_nodes', 'categories', ['category_id'], ['id'])

    op.drop_constraint('step_items_step_id_fkey', 'step_items', type_='foreignkey')
    op.create_foreign_key('step_items_step_id_fkey', 'step_items', 'recipe_steps', ['step_id'], ['id'])

    op.drop_constraint('step_ingredients_step_id_fkey', 'step_ingredients', type_='foreignkey')
    op.create_foreign_key('step_ingredients_step_id_fkey', 'step_ingredients', 'recipe_steps', ['step_id'], ['id'])

    op.drop_constraint('recipe_steps_recipe_id_fkey', 'recipe_steps', type_='foreignkey')
    op.create_foreign_key('recipe_steps_recipe_id_fkey', 'recipe_steps', 'recipes', ['recipe_id'], ['id'])

    op.drop_constraint('recipe_ingredients_recipe_id_fkey', 'recipe_ingredients', type_='foreignkey')
    op.create_foreign_key('recipe_ingredients_recipe_id_fkey', 'recipe_ingredients', 'recipes', ['recipe_id'], ['id'])