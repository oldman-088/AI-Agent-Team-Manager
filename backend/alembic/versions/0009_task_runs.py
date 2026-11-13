"""Add durable manual text-run metadata with one unresolved run per task.

Revision ID: 0009
Revises: 0008
"""
from alembic import op
import sqlalchemy as sa

revision = '0009'
down_revision = '0008'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('task_runs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('tasks.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('agent_id', sa.Integer(), sa.ForeignKey('agents.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('model', sa.String(200), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('input_tokens', sa.Integer(), nullable=True),
        sa.Column('output_tokens', sa.Integer(), nullable=True),
        sa.CheckConstraint("status IN ('running', 'succeeded', 'uncertain', 'resolved')", name='ck_task_runs_status'),
    )
    active = sa.text("status IN ('running', 'uncertain')")
    op.create_index('uq_task_runs_active_task', 'task_runs', ['task_id'], unique=True, sqlite_where=active, postgresql_where=active)


def downgrade():
    if op.get_bind().execute(sa.text('SELECT COUNT(*) FROM task_runs')).scalar_one():
        raise RuntimeError('Cannot downgrade while task run history exists; back up and resolve explicitly first')
    op.drop_index('uq_task_runs_active_task', table_name='task_runs')
    op.drop_table('task_runs')
