import { expect, it, vi } from 'vitest';
import { listEvents } from './events';

it('retrieves events and reports failures', async () => {
  expect(await listEvents(vi.fn().mockResolvedValue({ok: true, json: async () => []}))).toEqual([]);
  await expect(listEvents(vi.fn().mockResolvedValue({ok: false}))).rejects.toThrow('Could not load activity');
});
