import { useEffect, useState, type FormEvent } from 'react';
import { createRoot } from 'react-dom/client';
import { fetchHealth, type Health } from './health';
import { createProject, listProjects, type Project } from './projects';
import { createAgent, listAgents, type Agent } from './agents';
import './style.css';

function App() {
  const [health, setHealth] = useState<Health>('checking');
  const [projects, setProjects] = useState<Project[]>([]);
  const [error, setError] = useState('');
  const [agents, setAgents] = useState<Agent[]>([]);
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
      try { const [projectList, agentList] = await Promise.all([listProjects(), listAgents()]); setProjects(projectList); setAgents(agentList); } catch (e) { setError(e instanceof Error ? e.message : 'Unable to load projects'); }
    } else { setProjects([]); setAgents([]); }
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
  return <main><header><p className="eyebrow">AATM · LOCAL CONTROL CENTER</p><h1>Team workspace</h1><p>A foundation for managing AI engineering teams.</p></header>{error && <p role="alert">{error}</p>}<section aria-labelledby="status-heading"><h2 id="status-heading">System status</h2><p role="status">Backend and database: <strong>{health === 'ready' ? 'Ready' : health === 'checking' ? 'Checking…' : 'Not ready'}</strong></p><button onClick={() => void refresh()}>Refresh status and projects</button><p>Readiness indicates database connectivity only; it does not validate migrations or production security.</p></section><section aria-labelledby="projects-heading"><h2 id="projects-heading">Projects</h2><p>Manage basic project records in the configured database.</p><form onSubmit={submit}><label>Project name<input value={name} onChange={e => setName(e.target.value)} required maxLength={200} /></label><label>Description<textarea value={description} onChange={e => setDescription(e.target.value)} maxLength={4000} /></label><button disabled={saving || health !== 'ready'}>{saving ? 'Saving…' : 'Create project'}</button></form>{projects.length ? <ul>{projects.map(project => <li key={project.id}><strong>{project.name}</strong> <span>· {project.status}</span>{project.description && <p>{project.description}</p>}</li>)}</ul> : <p>No projects loaded.</p>}</section><section aria-labelledby="agents-heading"><h2 id="agents-heading">Agent configurations</h2><p>These are configuration records only. No agent process or lifecycle is implemented.</p><form onSubmit={submitAgent}><label>Agent name<input value={agentName} onChange={e => setAgentName(e.target.value)} required maxLength={100} /></label><label>Role<input value={role} onChange={e => setRole(e.target.value)} required maxLength={200} /></label><label>Project<select value={projectId} onChange={e => setProjectId(e.target.value)}><option value="">Unassigned</option>{projects.map(project => <option key={project.id} value={project.id}>{project.name}</option>)}</select></label><button disabled={savingAgent || health !== 'ready'}>{savingAgent ? 'Saving…' : 'Create configuration'}</button></form>{agents.length ? <ul>{agents.map(agent => <li key={agent.id}><strong>{agent.name}</strong> · {agent.role} <span>— execution not implemented</span></li>)}</ul> : <p>No agent configurations loaded.</p>}</section><section><h2>Under construction</h2><p>Agent execution, providers and orchestration are not yet available in this dashboard. Project editing and deletion are currently available through the API only.</p></section></main>;
}

createRoot(document.getElementById('root')!).render(<App />);
