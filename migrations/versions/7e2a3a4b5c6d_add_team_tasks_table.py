"""add team tasks table

Revision ID: 7e2a3a4b5c6d
Revises: 96a19a53749c
Create Date: 2025-11-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e2a3a4b5c6d'
down_revision = '96a19a53749c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'team_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('point_type', sa.Enum('PJ', 'PCC', 'PS', name='pointtypeenum', native_enum=False), nullable=False),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('finished_at', sa.String(), nullable=True),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('team_tasks')

