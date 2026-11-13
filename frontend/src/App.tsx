import { setApiToken } from './api';
import { TaskRuns } from './TaskRuns';
import { UnresolvedRuns } from './UnresolvedRuns';
import { TaskAssignment } from './TaskAssignment';
import { TaskDetails } from './TaskDetails';
import { useEffect, useRef, useState, type FormEvent } from 'react';
import { fetchHealth, type Health } from './health';
import { createProject, listProjects, type Project } from './projects';
import { createAgent, listAgents, type Agent } from './agents';
import { listEvents, type ActivityEvent } from './events';
import { completeTask, createTask, listReadyTasks, listTasks, type Task } from './tasks';
import { direction, eventLabel, messages, statusLabel, type Locale } from './i18n/messages';

type ErrorKey = 'loadError' | 'projectError' | 'agentError' | 'taskError' | 'completeError';

export function App() {
  const [locale, setLocale] = useState<Locale>('en');
  const t = messages[locale];
  const [health, setHealth] = useState<Health>('checking');
  const [projects, setProjects] = useState<Project[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [events, setEvents] = useState<ActivityEvent[]>([]);
  const [readyTasks, setReadyTasks] = useState<Task[]>([]);
  const [error, setError] = useState<ErrorKey | null>(null);
  const [tokenInput, setTokenInput] = useState('');
  const [tokenConfigured, setTokenConfigured] = useState(false);
  const refreshSequence = useRef(0);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [agentName, setAgentName] = useState('');
  const [role, setRole] = useState('');
  const [projectId, setProjectId] = useState('');
  const [taskTitle, setTaskTitle] = useState('');
  const [taskProject, setTaskProject] = useState('');
  const [selectedTask, setSelectedTask] = useState('');
  const [saving, setSaving] = useState(false);
  const [savingAgent, setSavingAgent] = useState(false);
  const [savingTask, setSavingTask] = useState(false);
  const [completingId, setCompletingId] = useState<number | null>(null);

  useEffect(() => {
    document.documentElement.lang = locale;
    document.documentElement.dir = direction(locale);
  }, [locale]);

  async function refresh() {
    const sequence = ++refreshSequence.current;
    setHealth('checking');
    setError(null);
    const state = await fetchHealth();
    if (sequence !== refreshSequence.current) return;
    setHealth(state);
    if (state === 'ready') {
      try {
        const [projectList, agentList, taskList, activity, readyList] = await Promise.all([listProjects(), listAgents(), listTasks(), listEvents(), listReadyTasks()]);
        if (sequence !== refreshSequence.current) return;
        setProjects(projectList); setAgents(agentList); setTasks(taskList); setEvents(activity); setReadyTasks(readyList);
      } catch {
        if (sequence !== refreshSequence.current) return;
        setProjects([]); setAgents([]); setTasks([]); setEvents([]); setReadyTasks([]); setError('loadError');
      }
    } else { setProjects([]); setAgents([]); setTasks([]); setEvents([]); setReadyTasks([]); }
  }
  useEffect(() => { void refresh(); }, []);

  function submitToken(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setApiToken(tokenInput); setTokenConfigured(Boolean(tokenInput)); setTokenInput('');
    setProjects([]); setAgents([]); setTasks([]); setEvents([]); setReadyTasks([]); setSelectedTask('');
    void refresh();
  }
  async function submitProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSaving(true); setError(null);
    try { await createProject(name, description); setName(''); setDescription(''); await refresh(); }
    catch { setError('projectError'); }
    finally { setSaving(false); }
  }
  async function submitAgent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSavingAgent(true); setError(null);
    try { await createAgent(agentName, role, projectId ? Number(projectId) : null); setAgentName(''); setRole(''); setProjectId(''); await refresh(); }
    catch { setError('agentError'); }
    finally { setSavingAgent(false); }
  }
  async function submitTask(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSavingTask(true); setError(null);
    try { await createTask(Number(taskProject), taskTitle); setTaskTitle(''); setTaskProject(''); await refresh(); }
    catch { setError('taskError'); }
    finally { setSavingTask(false); }
  }

  async function finishTask(id: number) {
    setCompletingId(id); setError(null);
    try { await completeTask(id); await refresh(); }
    catch { setError('completeError'); }
    finally { setCompletingId(null); }
  }

  return <main>
    <header>
      <label className="language">{t.language}<select value={locale} onChange={e => setLocale(e.target.value as Locale)}>
        <option value="en" lang="en">English</option><option value="ar" lang="ar">العربية</option><option value="fa" lang="fa">فارسی</option>
      </select></label>
      <p className="eyebrow">{t.eyebrow}</p><h1>{t.title}</h1><p>{t.subtitle}</p>
    </header>
    {error && <p role="alert">{t[error]}</p>}
    <section aria-labelledby="status-heading"><h2 id="status-heading">{t.system}</h2>
      <p role="status">{t.backend}: <strong>{health === 'ready' ? t.ready : health === 'checking' ? t.checking : t.notReady}</strong></p>
      <button onClick={() => void refresh()}>{t.refresh}</button><p>{t.readiness}</p>
      <p>{t.tokenHelp}</p><form onSubmit={submitToken}><label>{t.apiToken}<input type="password" autoComplete="off" value={tokenInput} onChange={e => setTokenInput(e.target.value)} maxLength={256} /></label><button>{t.applyToken}</button></form><p>{tokenConfigured ? t.tokenSet : t.tokenUnset}</p>
    </section>
    <section aria-labelledby="projects-heading"><h2 id="projects-heading">{t.projects}</h2><p>{t.projectsHelp}</p>
      <form onSubmit={submitProject}>
        <label>{t.projectName}<input dir="auto" value={name} onChange={e => setName(e.target.value)} required maxLength={200} /></label>
        <label>{t.description}<textarea dir="auto" value={description} onChange={e => setDescription(e.target.value)} maxLength={4000} /></label>
        <button disabled={saving || health !== 'ready'}>{saving ? t.saving : t.createProject}</button>
      </form>
      {projects.length ? <ul>{projects.map(project => <li key={project.id}><strong><bdi>{project.name}</bdi></strong> · {statusLabel(locale, project.status)}{project.description && <p dir="auto">{project.description}</p>}</li>)}</ul> : <p>{t.noProjects}</p>}
    </section>
    <section aria-labelledby="agents-heading"><h2 id="agents-heading">{t.agents}</h2><p>{t.agentsHelp}</p>
      <form onSubmit={submitAgent}>
        <label>{t.agentName}<input dir="auto" value={agentName} onChange={e => setAgentName(e.target.value)} required maxLength={100} /></label>
        <label>{t.role}<input dir="auto" value={role} onChange={e => setRole(e.target.value)} required maxLength={200} /></label>
        <label>{t.project}<select value={projectId} onChange={e => setProjectId(e.target.value)}><option value="">{t.unassigned}</option>{projects.map(project => <option key={project.id} value={project.id}>{project.name}</option>)}</select></label>
        <button disabled={savingAgent || health !== 'ready'}>{savingAgent ? t.saving : t.createAgent}</button>
      </form>
      {agents.length ? <ul>{agents.map(agent => <li key={agent.id}><strong><bdi>{agent.name}</bdi></strong> · <bdi>{agent.role}</bdi> — {t.noExecution}</li>)}</ul> : <p>{t.noAgents}</p>}
    </section>
    <section aria-labelledby="tasks-heading"><h2 id="tasks-heading">{t.tasks}</h2><p>{t.tasksHelp}</p><p>{t.completeHelp}</p>
      <form onSubmit={submitTask}>
        <label>{t.project}<select required value={taskProject} onChange={e => setTaskProject(e.target.value)}><option value="">{t.selectProject}</option>{projects.map(project => <option key={project.id} value={project.id}>{project.name}</option>)}</select></label>
        <label>{t.taskTitle}<input dir="auto" value={taskTitle} onChange={e => setTaskTitle(e.target.value)} required maxLength={200} /></label>
        <button disabled={savingTask || health !== 'ready' || !projects.length}>{savingTask ? t.saving : t.createTask}</button>
      </form>
      {tasks.length ? <ul>{tasks.map(task => <li key={task.id}><strong><bdi>{task.title}</bdi></strong> · {statusLabel(locale, task.status)} · <bdi>{projects.find(project => project.id === task.project_id)?.name ?? `#${task.project_id}`}</bdi>{task.status === 'pending' && <button className="task-action" disabled={completingId !== null} onClick={() => void finishTask(task.id)}>{t.manualComplete}</button>}</li>)}</ul> : <p>{t.noTasks}</p>}
      <h3>{t.details}</h3>
      <label>{t.selectTask}<select value={selectedTask} onChange={e => setSelectedTask(e.target.value)}><option value="">{t.chooseTask}</option>{tasks.map(task => <option key={task.id} value={task.id}>{task.title} (#{task.id})</option>)}</select></label>
      {tasks.find(task => String(task.id) === selectedTask) && <><TaskAssignment key={`assignment-${selectedTask}`} task={tasks.find(task => String(task.id) === selectedTask)!} agents={agents} locale={locale} onChanged={refresh} /><TaskDetails key={selectedTask} task={tasks.find(task => String(task.id) === selectedTask)!} tasks={tasks} locale={locale} onChanged={refresh} /><TaskRuns key={`runs-${selectedTask}`} taskId={Number(selectedTask)} locale={locale} refreshVersion={tasks} /></>}
    </section>
    <UnresolvedRuns locale={locale} refreshVersion={readyTasks} />
    <section aria-labelledby="ready-tasks-heading"><h2 id="ready-tasks-heading">{t.readyTasks}</h2><p>{t.readyTasksHelp}</p>
      {readyTasks.length ? <ul>{readyTasks.map(task => <li key={task.id}><bdi>{task.title}</bdi> · <bdi>#{task.id}</bdi> · <bdi>{projects.find(project => project.id === task.project_id)?.name ?? `#${task.project_id}`}</bdi></li>)}</ul> : <p>{t.noReadyTasks}</p>}
    </section>
    <section aria-labelledby="activity-heading"><h2 id="activity-heading">{t.activity}</h2><p>{t.activityHelp}</p>
      {events.length ? <ul>{events.map(event => <li key={event.id}>{eventLabel(locale, event.event_type)} · <bdi>{event.created_at}</bdi>{event.task_id !== null && <> · <bdi>#{event.task_id}</bdi></>}</li>)}</ul> : <p>{t.noActivity}</p>}
    </section>
    <section><h2>{t.underConstruction}</h2><p>{t.limitations}</p></section>
  </main>;
}
