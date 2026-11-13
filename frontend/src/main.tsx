import { useEffect, useState, type FormEvent } from 'react';
import { createRoot } from 'react-dom/client';
import { fetchHealth, type Health } from './health';
import { createProject, listProjects, type Project } from './projects';
import { createAgent, listAgents, type Agent } from './agents';
import { createTask, listTasks, type Task } from './tasks';
import './style.css';

function App() {
  const [health, setHealth] = useState<Health>('checking');
  const [projects, setProjects] = useState<Project[]>([]);
  const [error, setError] = useState('');
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [taskTitle, setTaskTitle] = useState('');
  const [taskProject, setTaskProject] = useState('');
  const [savingTask, setSavingTask] = useState(false);
  const [agentName, setAgentName] = useState('');
  const [role, setRole] = useState('');
  const [projectId, setProjectId] = useState('');
  const [savingAgent, setSavingAgent] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);
  async function refresh() {
    setHealth('checking'); setError('');
    const state = await fetchHealth(); setHealth(state);
    if (state === 'ready') {
      try { const [projectList, agentList, taskList] = await Promise.all([listProjects(), listAgents(), listTasks()]); setProjects(projectList); setAgents(agentList); setTasks(taskList); } catch (e) { setError(e instanceof Error ? e.message : 'Unable to load projects'); }
    } else { setProjects([]); setAgents([]); setTasks([]); }
  }
  useEffect(() => { void refresh(); }, []);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSaving(true); setError('');
    try { await createProject(name, description); setName(''); setDescription(''); await refresh(); }
    catch (e) { setError(e instanceof Error ? e.message : 'Unable to create project'); }
    finally { setSaving(false); }
  }
  async function submitAgent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSavingAgent(true); setError('');
    try { await createAgent(agentName, role, projectId ? Number(projectId) : null); setAgentName(''); setRole(''); setProjectId(''); await refresh(); }
    catch (e) { setError(e instanceof Error ? e.message : 'Unable to create agent'); }
    finally { setSavingAgent(false); }
  }
  async function submitTask(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSavingTask(true); setError('');
    try { await createTask(Number(taskProject), taskTitle); setTaskTitle(''); setTaskProject(''); await refresh(); }
    catch (e) { setError(e instanceof Error ? e.message : 'Unable to create task'); }
    finally { setSavingTask(false); }
  }
  return <main><header><p className="eyebrow">AATM · LOCAL CONTROL CENTER</p><h1>Team workspace</h1><p>A foundation for managing AI engineering teams.</p></header>{error && <p role="alert">{error}</p>}<section aria-labelledby="status-heading"><h2 id="status-heading">System status</h2><p role="status">Backend and database: <strong>{health === 'ready' ? 'Ready' : health === 'checking' ? 'Checking…' : 'Not ready'}</strong></p><button onClick={() => void refresh()}>Refresh status and projects</button><p>Readiness indicates database connectivity only; it does not validate migrations or production security.</p></section><section aria-labelledby="projects-heading"><h2 id="projects-heading">Projects</h2><p>Manage basic project records in the configured database.</p><form onSubmit={submit}><label>Project name<input value={name} onChange={e => setName(e.target.value)} required maxLength={200} /></label><label>Description<textarea value={description} onChange={e => setDescription(e.target.value)} maxLength={4000} /></label><button disabled={saving || health !== 'ready'}>{saving ? 'Saving…' : 'Create project'}</button></form>{projects.length ? <ul>{projects.map(project => <li key={project.id}><strong>{project.name}</strong> <span>· {project.status}</span>{project.description && <p>{project.description}</p>}</li>)}</ul> : <p>No projects loaded.</p>}</section><section aria-labelledby="agents-heading"><h2 id="agents-heading">Agent configurations</h2><p>These are configuration records only. No agent process or lifecycle is implemented.</p><form onSubmit={submitAgent}><label>Agent name<input value={agentName} onChange={e => setAgentName(e.target.value)} required maxLength={100} /></label><label>Role<input value={role} onChange={e => setRole(e.target.value)} required maxLength={200} /></label><label>Project<select value={projectId} onChange={e => setProjectId(e.target.value)}><option value="">Unassigned</option>{projects.map(project => <option key={project.id} value={project.id}>{project.name}</option>)}</select></label><button disabled={savingAgent || health !== 'ready'}>{savingAgent ? 'Saving…' : 'Create configuration'}</button></form>{agents.length ? <ul>{agents.map(agent => <li key={agent.id}><strong>{agent.name}</strong> · {agent.role} <span>— execution not implemented</span></li>)}</ul> : <p>No agent configurations loaded.</p>}</section><section aria-labelledby="tasks-heading"><h2 id="tasks-heading">Planning tasks</h2><p>Tasks are planning records only; agent assignment, dependencies and execution are not implemented.</p><form onSubmit={submitTask}><label>Project<select required value={taskProject} onChange={e => setTaskProject(e.target.value)}><option value="">Select a project</option>{projects.map(project => <option key={project.id} value={project.id}>{project.name}</option>)}</select></label><label>Task title<input value={taskTitle} onChange={e => setTaskTitle(e.target.value)} required maxLength={200} /></label><button disabled={savingTask || health !== 'ready' || !projects.length}>{savingTask ? 'Saving…' : 'Create task'}</button></form>{tasks.length ? <ul>{tasks.map(task => <li key={task.id}><strong>{task.title}</strong> · {task.status} · {projects.find(project => project.id === task.project_id)?.name ?? `Project #${task.project_id}`}</li>)}</ul> : <p>No tasks loaded.</p>}</section><section><h2>Under construction</h2><p>Agent execution, providers and orchestration are not yet available in this dashboard. Project editing and deletion are currently available through the API only.</p></section></main>;
}

createRoot(document.getElementById('root')!).render(<App />);
