from datetime import datetime, timedelta, timezone

from app.models import TaskRun
from app.services.run_inspection import heartbeat_state


def test_heartbeat_interpretation_is_advisory_and_handles_clock_skew():
    now = datetime.now(timezone.utc)
    run = TaskRun(status='running')
    assert heartbeat_state(run, now) == 'unknown'
    run.heartbeat_at = now - timedelta(seconds=30)
    assert heartbeat_state(run, now) == 'fresh'
    run.heartbeat_at = now - timedelta(seconds=31)
    assert heartbeat_state(run, now) == 'stale'
    run.heartbeat_at = (now + timedelta(seconds=31)).replace(tzinfo=None)
    assert heartbeat_state(run, now) == 'unknown'
    run.status = 'uncertain'
    assert heartbeat_state(run, now) == 'not_running'
