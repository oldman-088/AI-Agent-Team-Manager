"""Add agent configuration registry, not an execution state machine.

Revision ID: 0003
Revises: 0002
"""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'agents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('role', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('instructions', sa.Text(), nullable=False, server_default=''),
        sa.Column('provider', sa.String(100), nullable=False, server_default=''),
        sa.Column('model', sa.String(200), nullable=False, server_default=''),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete='SET NULL'), nullable=True),
    )
    op.create_index('ix_agents_project_id', 'agents', ['project_id'])


def downgrade():
    op.drop_index('ix_agents_project_id', table_name='agents')
    op.drop_table('agents')
