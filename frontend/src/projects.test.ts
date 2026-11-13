import { describe, expect, it, vi } from 'vitest';
import { createProject, listProjects } from './projects';

describe('projects API', () => {
  it('uses JSON and returns created projects', async () => {
    const fetcher = vi.fn().mockResolvedValue({ok: true, json: async () => ({id: 1, name: 'A'})});
    expect((await createProject('A', 'Details', fetcher)).id).toBe(1);
    expect(fetcher.mock.calls[0][1]).toMatchObject({method: 'POST', headers: {'Content-Type': 'application/json'}});
  });
  it('reports server errors', async () => {
    await expect(listProjects(vi.fn().mockResolvedValue({ok: false}))).rejects.toThrow('Could not load projects');
  });
});
