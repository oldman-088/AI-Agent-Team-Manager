/** @vitest-environment jsdom */
import { render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { UnresolvedRuns } from './UnresolvedRuns';

afterEach(() => vi.unstubAllGlobals());

it('displays advisory run metadata without exposing task content', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ok: true, json: async () => [{id: 2, project_id: 3, task_id: 4, agent_id: 5, status: 'uncertain', heartbeat_state: 'not_running'}]}));
  render(<UnresolvedRuns locale="en" refreshVersion={0} />);
  await waitFor(() => expect(screen.getByText(/Outcome uncertain/)).toBeTruthy());
  expect(screen.getByText(/stale or missing heartbeat/)).toBeTruthy();
  expect(screen.getByText(/#4/)).toBeTruthy();
});
