import { useEffect, useState, type FormEvent } from 'react';
import { getAssignment, setAssignment, type Task } from './tasks';
import type { Agent } from './agents';
import { messages, type Locale } from './i18n/messages';

export function TaskAssignment({task, agents, locale, onChanged}: {task: Task; agents: Agent[]; locale: Locale; onChanged: () => Promise<void>}) {
  const t = messages[locale];
  const [value, setValue] = useState('');
  const [loaded, setLoaded] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);
  useEffect(() => {
    let active = true;
    setLoaded(false);
    getAssignment(task.id).then(id => { if (active) { setValue(id === null ? '' : String(id)); setLoaded(true); } })
      .catch(() => { if (active) setError(true); });
    return () => { active = false; };
  }, [task.id]);
  const choices = agents.filter(agent => agent.project_id === task.project_id);
  const missing = value && !choices.some(agent => String(agent.id) === value);
  async function save(agentId: number | null) {
    setBusy(true); setError(false);
    try { await setAssignment(task.id, agentId); setValue(agentId === null ? '' : String(agentId)); await onChanged(); }
    catch { setError(true); }
    finally { setBusy(false); }
  }
  function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); void save(value ? Number(value) : null); }
  return <div><h4>{t.assignment}</h4><p>{t.assignmentHelp}</p>
    {error && <p role="alert">{t.assignmentError}</p>}
    {loaded && task.status !== 'pending' && <p>{value ? <>{t.selectAgent}: <bdi>{choices.find(agent => String(agent.id) === value)?.name ?? `${t.assignedMissing} (#${value})`}</bdi> <button disabled={busy} onClick={() => void save(null)}>{t.clearAssignment}</button></> : t.unassigned}</p>}
    {loaded && task.status === 'pending' && <form onSubmit={submit}><label>{t.selectAgent}<select value={value} onChange={e => setValue(e.target.value)} disabled={busy}>
      <option value="">{t.unassigned}</option>{missing && <option value={value}>{t.assignedMissing} (#{value})</option>}
      {choices.map(agent => <option key={agent.id} value={agent.id}>{agent.name} (#{agent.id})</option>)}
    </select></label><button disabled={busy}>{t.saveAssignment}</button></form>}
  </div>;
}
