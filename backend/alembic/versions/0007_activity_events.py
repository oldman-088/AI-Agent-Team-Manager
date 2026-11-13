"""Add minimal task activity history.

Revision ID: 0007
Revises: 0006
"""
from alembic import op
import sqlalchemy as sa

revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'activity_events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete='SET NULL'), nullable=True),
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('tasks.id', ondelete='SET NULL'), nullable=True),
        sa.Column('related_task_id', sa.Integer(), sa.ForeignKey('tasks.id', ondelete='SET NULL'), nullable=True),
        sa.Column('event_type', sa.String(40), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_activity_events_project_id_id', 'activity_events', ['project_id', 'id'])


def downgrade():
    # Do not silently delete existing operational history.
    if op.get_bind().execute(sa.text('SELECT COUNT(*) FROM activity_events')).scalar_one():
        raise RuntimeError('Cannot downgrade while activity events exist; back up and resolve them explicitly first')
    op.drop_index('ix_activity_events_project_id_id', table_name='activity_events')
    op.drop_table('activity_events')
