"""Serialize claims and prevent concurrent unresolved runs per agent.

Revision ID: 0011
Revises: 0010
"""
from alembic import op
import sqlalchemy as sa

revision = '0011'
down_revision = '0010'
branch_labels = None
depends_on = None


def upgrade():
    # Refuse to silently erase or resolve pre-existing ambiguous runs.
    duplicate = op.get_bind().execute(sa.text("SELECT agent_id FROM task_runs WHERE status IN ('running', 'uncertain') GROUP BY agent_id HAVING COUNT(*) > 1 LIMIT 1")).first()
    if duplicate:
        raise RuntimeError('Cannot upgrade while an agent has multiple unresolved runs; investigate first')
    op.create_table('worker_capacity_lock',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.CheckConstraint('id = 1', name='ck_worker_capacity_singleton'))
    op.execute(sa.text('INSERT INTO worker_capacity_lock (id) VALUES (1)'))
    active = sa.text("status IN ('running', 'uncertain')")
    op.create_index('uq_task_runs_active_agent', 'task_runs', ['agent_id'], unique=True, sqlite_where=active, postgresql_where=active)


def downgrade():
    if op.get_bind().execute(sa.text("SELECT COUNT(*) FROM task_runs WHERE status IN ('running', 'uncertain')")).scalar_one():
        raise RuntimeError('Cannot downgrade while unresolved worker runs exist; investigate first')
    op.drop_index('uq_task_runs_active_agent', table_name='task_runs')
    op.drop_table('worker_capacity_lock')
