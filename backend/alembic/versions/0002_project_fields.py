"""Add project description and status without deleting existing projects.

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('projects') as batch:
        batch.add_column(sa.Column('description', sa.Text(), nullable=False, server_default=''))
        batch.add_column(sa.Column('status', sa.String(20), nullable=False, server_default='planned'))
        batch.create_check_constraint('ck_projects_status', "status IN ('planned', 'active', 'paused', 'completed', 'archived')")


def downgrade():
    with op.batch_alter_table('projects') as batch:
        batch.drop_constraint('ck_projects_status', type_='check')
        batch.drop_column('status')
        batch.drop_column('description')
