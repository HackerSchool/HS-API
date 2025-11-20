"""add contributors to team tasks

Revision ID: ab12cd34ef56
Revises: 7e2a3a4b5c6d
Create Date: 2025-11-09 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab12cd34ef56'
down_revision = '7e2a3a4b5c6d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'team_tasks',
        sa.Column('contributors', sa.String(), nullable=False, server_default='')
    )
    op.execute("UPDATE team_tasks SET contributors = '' WHERE contributors IS NULL")


def downgrade():
    op.drop_column('team_tasks', 'contributors')

