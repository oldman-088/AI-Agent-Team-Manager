import { useEffect, useState } from 'react';
import { messages, type Locale } from './i18n/messages';

interface TaskRun { id: number; agent_id: number; status: 'running' | 'succeeded' | 'uncertain' | 'resolved'; model: string; started_at: string; input_tokens: number | null; output_tokens: number | null }

export function TaskRuns({taskId, locale, refreshVersion}: {taskId: number; locale: Locale; refreshVersion: unknown}) {
  const t = messages[locale];
  const [runs, setRuns] = useState<TaskRun[] | null>(null);
  const [error, setError] = useState(false);
  useEffect(() => {
    let active = true;
    setRuns(null); setError(false);
    fetch(`/api/tasks/${taskId}/runs`).then(response => {
      if (!response.ok) throw new Error('Cannot load runs');
      return response.json();
    }).then(data => { if (active) setRuns(data); }).catch(() => { if (active) setError(true); });
    return () => { active = false; };
  }, [taskId, refreshVersion]);
  const labels = {running: t.runRunning, succeeded: t.runSucceeded, uncertain: t.runUncertain, resolved: t.runResolved};
  return <div><h4>{t.runs}</h4><p>{t.runsHelp}</p>
    {error ? <p role="alert">{t.runsError}</p> : runs === null ? <p>{t.loadingDetails}</p> : runs.length ? <ul>{runs.map(run => <li key={run.id}><bdi>#{run.id}</bdi> · {labels[run.status]} · <bdi>{run.model}</bdi> · <bdi>{run.started_at}</bdi></li>)}</ul> : <p>{t.noRuns}</p>}
  </div>;
}
