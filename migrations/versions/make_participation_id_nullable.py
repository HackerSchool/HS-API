"""make participation_id nullable

Revision ID: make_participation_nullable
Revises: ab12cd34ef56
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'make_participation_nullable'
down_revision = 'ab12cd34ef56'
branch_labels = None
depends_on = None


def upgrade():
    # Make participation_id nullable to allow tasks without projects
    op.alter_column('tasks', 'participation_id',
                    existing_type=sa.Integer(),
                    nullable=True)
    
    # Add member_id column to allow tasks without participation
    op.add_column('tasks', sa.Column('member_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_tasks_member_id', 'tasks', 'members', ['member_id'], ['id'])


def downgrade():
    # Remove member_id column
    op.drop_constraint('fk_tasks_member_id', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'member_id')
    
    # Revert participation_id to NOT NULL
    # First, we need to delete or assign tasks without participations
    op.execute("DELETE FROM tasks WHERE participation_id IS NULL")
    op.alter_column('tasks', 'participation_id',
                    existing_type=sa.Integer(),
                    nullable=False)
