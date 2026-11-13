import { describe, expect, it, vi } from 'vitest';
import { fetchHealth } from './health';

describe('readiness', () => {
  it('reports readiness from the server', async () => {
    expect(await fetchHealth(vi.fn().mockResolvedValue({ok: true}))).toBe('ready');
    expect(await fetchHealth(vi.fn().mockResolvedValue({ok: false}))).toBe('not-ready');
  });
  it('handles network failures', async () => {
    expect(await fetchHealth(vi.fn().mockRejectedValue(new Error('offline')))).toBe('not-ready');
  });
});
