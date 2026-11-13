"""Add project-scoped task dependency edges.

Revision ID: 0005
Revises: 0004
"""
from alembic import op
import sqlalchemy as sa

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('uq_tasks_id_project_id', 'tasks', ['id', 'project_id'], unique=True)
    op.create_table(
        'task_dependencies',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('depends_on_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('task_id', 'depends_on_id'),
        sa.ForeignKeyConstraint(['task_id', 'project_id'], ['tasks.id', 'tasks.project_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['depends_on_id', 'project_id'], ['tasks.id', 'tasks.project_id'], ondelete='RESTRICT'),
        sa.CheckConstraint('task_id != depends_on_id', name='ck_dependency_not_self'),
    )
    op.create_index('ix_dependencies_project_id', 'task_dependencies', ['project_id'])


def downgrade():
    op.drop_index('ix_dependencies_project_id', table_name='task_dependencies')
    op.drop_table('task_dependencies')
    op.drop_index('uq_tasks_id_project_id', table_name='tasks')
