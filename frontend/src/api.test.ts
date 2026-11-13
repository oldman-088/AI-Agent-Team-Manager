import { afterEach, expect, it, vi } from 'vitest';
import { apiFetch, setApiToken } from './api';

afterEach(() => { setApiToken(''); vi.unstubAllGlobals(); });

it('attaches token only to relative API URLs and preserves headers', async () => {
  const fetcher = vi.fn().mockResolvedValue({ok: true});
  vi.stubGlobal('fetch', fetcher);
  setApiToken('local-test-token');
  await apiFetch('/api/tasks', {method: 'POST', headers: {'Content-Type': 'application/json'}});
  const headers = fetcher.mock.calls[0][1].headers as Headers;
  expect(headers.get('Authorization')).toBe('Bearer local-test-token');
  expect(headers.get('Content-Type')).toBe('application/json');
  await apiFetch('https://example.test/api/tasks');
  expect(fetcher.mock.calls[1][1]).toBeUndefined();
  await apiFetch('/health/ready');
  expect(fetcher.mock.calls[2][1]).toBeUndefined();
  setApiToken('');
  await apiFetch('/api/tasks');
  expect(fetcher.mock.calls[3][1]).toBeUndefined();
});
