"""Allow explicit manual completion after dependencies are satisfied.

Revision ID: 0006
Revises: 0005
"""
from alembic import op
import sqlalchemy as sa

revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('tasks') as batch:
        batch.drop_constraint('ck_tasks_status', type_='check')
        batch.create_check_constraint('ck_tasks_status', "status IN ('pending', 'cancelled', 'completed')")


def downgrade():
    # Never silently rewrite completed records to another state.
    completed = op.get_bind().execute(sa.text("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")).scalar_one()
    if completed:
        raise RuntimeError('Cannot downgrade while completed tasks exist; back up and resolve them explicitly first')
    with op.batch_alter_table('tasks') as batch:
        batch.drop_constraint('ck_tasks_status', type_='check')
        batch.create_check_constraint('ck_tasks_status', "status IN ('pending', 'cancelled')")
