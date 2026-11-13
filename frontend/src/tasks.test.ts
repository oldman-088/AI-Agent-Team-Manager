import { describe, expect, it, vi } from 'vitest';
import { createTask, listTasks } from './tasks';

describe('tasks API', () => {
  it('creates a project-scoped planning task', async () => {
    const fetcher = vi.fn().mockResolvedValue({ok: true, json: async () => ({id: 1, status: 'pending'})});
    expect((await createTask(2, 'Plan', fetcher)).status).toBe('pending');
    expect(JSON.parse(fetcher.mock.calls[0][1].body)).toEqual({project_id: 2, title: 'Plan'});
  });
  it('reports server errors', async () => {
    await expect(listTasks(vi.fn().mockResolvedValue({ok: false}))).rejects.toThrow('Could not load tasks');
  });
});

it('sends JSON for dependency addition and no body for removal', async () => {
  const { changeDependency } = await import('./tasks');
  const fetcher = vi.fn().mockResolvedValue({ok: true});
  await changeDependency(1, 2, true, fetcher);
  expect(fetcher).toHaveBeenCalledWith('/api/tasks/1/dependencies/2', {method: 'PUT', headers: {'Content-Type': 'application/json'}, body: '{}'});
  await changeDependency(1, 2, false, fetcher);
  expect(fetcher).toHaveBeenLastCalledWith('/api/tasks/1/dependencies/2', {method: 'DELETE'});
});

it('loads ready tasks and surfaces server errors', async () => {
  const { listReadyTasks } = await import('./tasks');
  const fetcher = vi.fn().mockResolvedValue({ok: true, json: async () => []});
  expect(await listReadyTasks(fetcher)).toEqual([]);
  expect(fetcher).toHaveBeenCalledWith('/api/tasks/ready');
  await expect(listReadyTasks(vi.fn().mockResolvedValue({ok: false}))).rejects.toThrow('Could not load ready tasks');
});
