import { describe, expect, it, vi } from 'vitest';
import { createAgent, listAgents } from './agents';

describe('agents API', () => {
  it('creates a configuration with optional project', async () => {
    const fetcher = vi.fn().mockResolvedValue({ok: true, json: async () => ({id: 1, name: 'Ada'})});
    expect((await createAgent('Ada', 'Developer', 2, fetcher)).id).toBe(1);
    expect(JSON.parse(fetcher.mock.calls[0][1].body)).toEqual({name: 'Ada', role: 'Developer', project_id: 2});
  });
  it('reports server errors', async () => {
    await expect(listAgents(vi.fn().mockResolvedValue({ok: false}))).rejects.toThrow('Could not load agents');
  });
});
