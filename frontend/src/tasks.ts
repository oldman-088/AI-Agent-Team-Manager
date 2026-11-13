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
