export interface Project { id: number; name: string; description: string; status: string }

export async function listProjects(fetcher: typeof fetch = fetch): Promise<Project[]> {
  const response = await fetcher('/api/projects');
  if (!response.ok) throw new Error('Could not load projects. Check the backend and database.');
  return response.json();
}

export async function createProject(name: string, description: string, fetcher: typeof fetch = fetch): Promise<Project> {
  const response = await fetcher('/api/projects', {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name, description}),
  });
  if (!response.ok) throw new Error('Could not create project. Check the form and database.');
  return response.json();
}
