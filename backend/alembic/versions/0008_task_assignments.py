"""Add project-scoped planning assignments.

Revision ID: 0008
Revises: 0007
"""
from alembic import op
import sqlalchemy as sa

revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('uq_agents_id_project_id', 'agents', ['id', 'project_id'], unique=True)
    op.create_table('task_assignments',
        sa.Column('task_id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['task_id', 'project_id'], ['tasks.id', 'tasks.project_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['agent_id', 'project_id'], ['agents.id', 'agents.project_id'], ondelete='RESTRICT'),
    )
    op.create_index('ix_task_assignments_agent_id', 'task_assignments', ['agent_id'])


def downgrade():
    if op.get_bind().execute(sa.text('SELECT COUNT(*) FROM task_assignments')).scalar_one():
        raise RuntimeError('Cannot downgrade while task assignments exist; back up and resolve them explicitly first')
    op.drop_index('ix_task_assignments_agent_id', table_name='task_assignments')
    op.drop_table('task_assignments')
    op.drop_index('uq_agents_id_project_id', table_name='agents')
