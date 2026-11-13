import { useEffect, useState, type FormEvent } from 'react';
import { createRoot } from 'react-dom/client';
import { fetchHealth, type Health } from './health';
import { createProject, listProjects, type Project } from './projects';
import './style.css';

function App() {
  const [health, setHealth] = useState<Health>('checking');
  const [projects, setProjects] = useState<Project[]>([]);
  const [error, setError] = useState('');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);
  async function refresh() {
    setHealth('checking'); setError('');
    const state = await fetchHealth(); setHealth(state);
    if (state === 'ready') {
      try { setProjects(await listProjects()); } catch (e) { setError(e instanceof Error ? e.message : 'Unable to load projects'); }
    } else { setProjects([]); }
  }
  useEffect(() => { void refresh(); }, []);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSaving(true); setError('');
    try { await createProject(name, description); setName(''); setDescription(''); await refresh(); }
    catch (e) { setError(e instanceof Error ? e.message : 'Unable to create project'); }
    finally { setSaving(false); }
  }
  return <main><header><p className="eyebrow">AATM · LOCAL CONTROL CENTER</p><h1>Team workspace</h1><p>A foundation for managing AI engineering teams.</p></header><section aria-labelledby="status-heading"><h2 id="status-heading">System status</h2><p role="status">Backend and database: <strong>{health === 'ready' ? 'Ready' : health === 'checking' ? 'Checking…' : 'Not ready'}</strong></p><button onClick={() => void refresh()}>Refresh status and projects</button><p>Readiness indicates database connectivity only; it does not validate migrations or production security.</p></section><section aria-labelledby="projects-heading"><h2 id="projects-heading">Projects</h2><p>Manage basic project records in the configured database.</p>{error && <p role="alert">{error}</p>}<form onSubmit={submit}><label>Project name<input value={name} onChange={e => setName(e.target.value)} required maxLength={200} /></label><label>Description<textarea value={description} onChange={e => setDescription(e.target.value)} maxLength={4000} /></label><button disabled={saving || health !== 'ready'}>{saving ? 'Saving…' : 'Create project'}</button></form>{projects.length ? <ul>{projects.map(project => <li key={project.id}><strong>{project.name}</strong> <span>· {project.status}</span>{project.description && <p>{project.description}</p>}</li>)}</ul> : <p>No projects loaded.</p>}</section><section><h2>Under construction</h2><p>Agent execution, providers and orchestration are not yet available in this dashboard. Project editing and deletion are currently available through the API only.</p></section></main>;
}

createRoot(document.getElementById('root')!).render(<App />);
