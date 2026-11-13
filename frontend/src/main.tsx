import { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { fetchHealth, type Health } from './health';
import './style.css';

function App() {
  const [health, setHealth] = useState<Health>('checking');
  useEffect(() => { let active = true; fetchHealth().then(value => { if (active) setHealth(value); }); return () => { active = false; }; }, []);
  return <main><header><p className="eyebrow">AATM · LOCAL CONTROL CENTER</p><h1>Team workspace</h1><p>A foundation for managing AI engineering teams.</p></header><section aria-labelledby="status-heading"><h2 id="status-heading">System status</h2><p role="status">Backend and database: <strong>{health === 'ready' ? 'Ready' : health === 'checking' ? 'Checking…' : 'Not ready'}</strong></p><button onClick={() => { setHealth('checking'); fetchHealth().then(setHealth); }}>Refresh status</button></section><section><h2>Under construction</h2><p>Agent execution, providers, projects, and orchestration are not yet available in this dashboard.</p><p>Readiness indicates database connectivity only; it does not validate migrations or production security.</p></section></main>;
}

createRoot(document.getElementById('root')!).render(<App />);
