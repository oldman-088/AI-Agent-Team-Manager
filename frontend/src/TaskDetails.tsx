import { useEffect, useState, type FormEvent } from 'react';
import { changeDependency, getDependencies, getReadiness, type Readiness, type Task } from './tasks';
import { messages, type Locale } from './i18n/messages';

export function TaskDetails({task, tasks, locale, onChanged}: {task: Task; tasks: Task[]; locale: Locale; onChanged: () => Promise<void>}) {
  const t = messages[locale];
  const [dependencies, setDependencies] = useState<number[] | null>(null);
  const [readiness, setReadiness] = useState<Readiness | null>(null);
  const [selected, setSelected] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);
  const [version, setVersion] = useState(0);

  useEffect(() => {
    let active = true;
    setDependencies(null); setReadiness(null);
    Promise.all([getDependencies(task.id), getReadiness(task.id)]).then(([edges, state]) => {
      if (active) { setDependencies(edges); setReadiness(state); }
    }).catch(() => { if (active) setError(true); });
    return () => { active = false; };
  }, [task.id, version, tasks]);

  async function change(id: number, add: boolean) {
    setBusy(true); setError(false);
    try { await changeDependency(task.id, id, add); setSelected(''); await onChanged(); }
    catch { setError(true); }
    finally { setVersion(v => v + 1); setBusy(false); }
  }
  function add(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (selected) void change(Number(selected), true);
  }
  const title = (id: number) => tasks.find(item => item.id === id)?.title ?? `${t.taskId} #${id}`;
  const available = tasks.filter(item => item.project_id === task.project_id && item.id !== task.id && !dependencies?.includes(item.id));
  return <div>
    <p>{t.snapshotHelp}</p>
    {error && <p role="alert">{t.dependencyError}</p>}
    {dependencies === null || readiness === null ? !error && <p role="status">{t.loadingDetails}</p> : <>
      <p>{readiness.ready ? t.readyTask : t.blockedTask}</p>
      {readiness.blocking_dependencies.length > 0 && <p>{t.blockers}: {readiness.blocking_dependencies.map(id => <span key={id}><bdi>{title(id)}</bdi> (#{id}) </span>)}</p>}
      <h4>{t.dependencies}</h4>
      {dependencies.length ? <ul>{dependencies.map(id => <li key={id}><bdi>{title(id)}</bdi> (#{id}) <button disabled={busy} aria-label={`${t.removeDependency}: ${title(id)} #${id}`} onClick={() => void change(id, false)}>{t.removeDependency}</button></li>)}</ul> : <p>{t.noDependencies}</p>}
      {task.status !== 'completed' && <form onSubmit={add}><label>{t.prerequisite}<select value={selected} onChange={e => setSelected(e.target.value)} required><option value="">{t.choosePrerequisite}</option>{available.map(item => <option key={item.id} value={item.id}>{item.title} (#{item.id})</option>)}</select></label><button disabled={busy || !selected}>{t.addDependency}</button></form>}
    </>}
  </div>;
}
