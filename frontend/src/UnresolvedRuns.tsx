import { useEffect, useState } from 'react';
import { apiFetch } from './api';
import { messages, type Locale } from './i18n/messages';

interface UnresolvedRun {
  id: number; project_id: number; task_id: number; agent_id: number;
  status: 'running' | 'uncertain'; heartbeat_state: 'fresh' | 'stale' | 'unknown' | 'not_running';
}

export function UnresolvedRuns({locale, refreshVersion}: {locale: Locale; refreshVersion: unknown}) {
  const t = messages[locale];
  const [runs, setRuns] = useState<UnresolvedRun[] | null>(null);
  const [error, setError] = useState(false);
  useEffect(() => {
    let active = true;
    setRuns(null); setError(false);
    apiFetch('/api/runs/unresolved?limit=100').then(response => {
      if (!response.ok) throw new Error('Unable to inspect unresolved runs');
      return response.json();
    }).then(data => { if (active) setRuns(data); }).catch(() => { if (active) setError(true); });
    return () => { active = false; };
  }, [refreshVersion]);
  const states = {fresh: t.heartbeatFresh, stale: t.heartbeatStale, unknown: t.heartbeatUnknown, not_running: t.heartbeatNotRunning};
  return <section><h2>{t.unresolvedRuns}</h2><p>{t.unresolvedHelp}</p>
    {error ? <p role="alert">{t.unresolvedError}</p> : runs === null ? <p>{t.loadingDetails}</p> : runs.length ?
      <ul>{runs.map(run => <li key={run.id}><bdi>#{run.id}</bdi> · {t.project} <bdi>#{run.project_id}</bdi> · {t.taskId} <bdi>#{run.task_id}</bdi> · {t.agentName} <bdi>#{run.agent_id}</bdi> · {run.status === 'running' ? t.runRunning : t.runUncertain} · {states[run.heartbeat_state] ?? t.heartbeatUnknown}</li>)}</ul> : <p>{t.noUnresolved}</p>}
  </section>;
}
