const $ = selector => document.querySelector(selector);
let agents = [];
async function api(path, method = 'GET', data) {
  const response = await fetch(path, {method, headers: method === 'GET' ? {} : {'Content-Type': 'application/json'}, body: data === undefined ? undefined : JSON.stringify(data)});
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Request failed');
  return result;
}
function node(tag, text, className) { const element = document.createElement(tag); element.textContent = text; if (className) element.className = className; return element; }
function option(value, label) { const o = node('option', label); o.value = value; return o; }
function agentOptions(select, selected = '') { select.replaceChildren(option('', 'Unassigned')); agents.forEach(a => select.append(option(String(a.id), a.name))); select.value = selected == null ? '' : String(selected); }
async function run(action) { try { $('#message').textContent = ''; await action(); await refresh(); } catch (e) { $('#message').textContent = e.message; } }
async function refresh() {
  const [list, tasks] = await Promise.all([api('/api/agents'), api('/api/tasks')]); agents = list;
  const assignment = $('#assignment'); const selected = assignment.value; agentOptions(assignment, selected);
  const agentList = $('#agents'); agentList.replaceChildren();
  if (!agents.length) agentList.append(node('p', 'No agents yet.', 'muted'));
  agents.forEach(a => { const item = node('div', '', 'item'); item.append(node('strong', a.name), node('p', a.role)); const del = node('button', 'Delete'); del.type = 'button'; del.onclick = () => { if (confirm('Delete this agent? Their tasks will become unassigned.')) run(() => api(`/api/agents/${a.id}`, 'DELETE')); }; item.append(del); agentList.append(item); });
  const taskList = $('#tasks'); taskList.replaceChildren();
  if (!tasks.length) taskList.append(node('p', 'No tasks yet.', 'muted'));
  tasks.forEach(t => { const item = node('div', '', 'item'); item.append(node('strong', t.title)); if (t.description) item.append(node('p', t.description)); const actions = node('div', '', 'actions'); const status = document.createElement('select'); status.setAttribute('aria-label', `Status for ${t.title}`); [['todo','To do'],['in_progress','In progress'],['done','Done']].forEach(([v,l]) => status.append(option(v,l))); status.value = t.status; status.onchange = () => run(() => api(`/api/tasks/${t.id}`, 'PATCH', {status: status.value})); const assignee = document.createElement('select'); assignee.setAttribute('aria-label', `Assignee for ${t.title}`); agentOptions(assignee, t.agent_id); assignee.onchange = () => run(() => api(`/api/tasks/${t.id}`, 'PATCH', {agent_id: assignee.value ? Number(assignee.value) : null})); const del = node('button', 'Delete'); del.type = 'button'; del.onclick = () => { if (confirm('Delete this task?')) run(() => api(`/api/tasks/${t.id}`, 'DELETE')); }; actions.append(status, assignee, del); item.append(actions); taskList.append(item); });
}
$('#agent-form').onsubmit = event => { event.preventDefault(); const form = event.currentTarget; const data = Object.fromEntries(new FormData(form)); run(async () => { await api('/api/agents', 'POST', data); form.reset(); }); };
$('#task-form').onsubmit = event => { event.preventDefault(); const form = event.currentTarget; const data = Object.fromEntries(new FormData(form)); data.agent_id = data.agent_id ? Number(data.agent_id) : null; run(async () => { await api('/api/tasks', 'POST', data); form.reset(); }); };
run(async () => {});
