// @vitest-environment jsdom
import { afterEach, expect, it, vi } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { TaskRuns } from './TaskRuns';

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
it('shows run outcome without treating it as task completion', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ok: true, json: async () => [{id: 4, agent_id: 2, status: 'succeeded', model: 'model', started_at: '2026-11-13', input_tokens: 3, output_tokens: 2}]}));
  render(<TaskRuns taskId={1} locale="en" refreshVersion={0} />);
  expect(await screen.findByText(/Response received/)).toBeTruthy();
  expect(screen.getByText(/not that the task is completed/)).toBeTruthy();
});
