"""Add optional worker heartbeat timestamps; old runs remain unknown.

Revision ID: 0010
Revises: 0009
"""
from alembic import op
import sqlalchemy as sa

revision = '0010'
down_revision = '0009'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('task_runs', sa.Column('heartbeat_at', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    # Do not silently discard evidence of worker activity.
    if op.get_bind().execute(sa.text('SELECT COUNT(*) FROM task_runs WHERE heartbeat_at IS NOT NULL')).scalar_one():
        raise RuntimeError('Cannot downgrade while heartbeat data exists; back up and resolve explicitly first')
    with op.batch_alter_table('task_runs') as batch:
        batch.drop_column('heartbeat_at')
