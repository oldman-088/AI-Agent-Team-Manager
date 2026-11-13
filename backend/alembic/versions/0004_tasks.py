"""Add project-scoped planning tasks.

Revision ID: 0004
Revises: 0003
"""
from alembic import op
import sqlalchemy as sa

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.CheckConstraint("status IN ('pending', 'cancelled')", name='ck_tasks_status'),
    )
    op.create_index('ix_tasks_project_id', 'tasks', ['project_id'])


def downgrade():
    op.drop_index('ix_tasks_project_id', table_name='tasks')
    op.drop_table('tasks')
