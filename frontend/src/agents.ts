export interface Agent { id: number; name: string; role: string; project_id: number | null; execution_status: 'not_implemented' }

export async function listAgents(fetcher: typeof fetch = fetch): Promise<Agent[]> {
  const response = await fetcher('/api/agents');
  if (!response.ok) throw new Error('Could not load agents. Check the backend and database.');
  return response.json();
}

export async function createAgent(name: string, role: string, projectId: number | null, fetcher: typeof fetch = fetch): Promise<Agent> {
  const response = await fetcher('/api/agents', {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name, role, project_id: projectId}),
  });
  if (!response.ok) throw new Error('Could not create agent. Check the form and database.');
  return response.json();
}
