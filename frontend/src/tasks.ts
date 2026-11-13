export interface Task { id: number; project_id: number; title: string; description: string; status: 'pending' | 'cancelled' | 'completed' }

export async function listTasks(fetcher: typeof fetch = fetch): Promise<Task[]> {
  const response = await fetcher('/api/tasks');
  if (!response.ok) throw new Error('Could not load tasks. Check the backend and database.');
  return response.json();
}

export async function createTask(projectId: number, title: string, fetcher: typeof fetch = fetch): Promise<Task> {
  const response = await fetcher('/api/tasks', {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({project_id: projectId, title}),
  });
  if (!response.ok) throw new Error('Could not create task. Check the form and database.');
  return response.json();
}

export async function completeTask(id: number, fetcher: typeof fetch = fetch): Promise<Task> {
  const response = await fetcher(`/api/tasks/${id}/complete`, {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: '{}',
  });
  if (!response.ok) throw new Error('Could not complete task');
  return response.json();
}

export interface Readiness { task_id: number; status: Task['status']; ready: boolean; blocking_dependencies: number[] }

export async function getDependencies(id: number, fetcher: typeof fetch = fetch): Promise<number[]> {
  const response = await fetcher(`/api/tasks/${id}/dependencies`);
  if (!response.ok) throw new Error('Could not load dependencies');
  return response.json();
}
export async function getReadiness(id: number, fetcher: typeof fetch = fetch): Promise<Readiness> {
  const response = await fetcher(`/api/tasks/${id}/readiness`);
  if (!response.ok) throw new Error('Could not load readiness');
  return response.json();
}
export async function changeDependency(id: number, dependencyId: number, add: boolean, fetcher: typeof fetch = fetch): Promise<void> {
  const response = await fetcher(`/api/tasks/${id}/dependencies/${dependencyId}`, {method: add ? 'PUT' : 'DELETE', ...(add ? {headers: {'Content-Type': 'application/json'}, body: '{}'} : {})});
  if (!response.ok) throw new Error('Could not change dependency');
}

export async function getAssignment(id: number, fetcher: typeof fetch = fetch): Promise<number | null> {
  const response = await fetcher(`/api/tasks/${id}/assignment`);
  if (!response.ok) throw new Error('Could not load assignment');
  return (await response.json()).agent_id;
}
export async function setAssignment(id: number, agentId: number | null, fetcher: typeof fetch = fetch): Promise<void> {
  const response = await fetcher(`/api/tasks/${id}/assignment`, {method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({agent_id: agentId})});
  if (!response.ok) throw new Error('Could not change assignment');
}

export async function listReadyTasks(fetcher: typeof fetch = fetch): Promise<Task[]> {
  const response = await fetcher('/api/tasks/ready');
  if (!response.ok) throw new Error('Could not load ready tasks');
  return response.json();
}
