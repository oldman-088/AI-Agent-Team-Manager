// @vitest-environment jsdom
import { afterEach, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { AgentClaim } from './AgentClaim';

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

it('looks up the selected agent and describes a claim without implying liveness', async () => {
  const fetcher = vi.fn().mockResolvedValue({ok: true, json: async () => ({agent_id: 3, claim_status: 'uncertain', run_id: 5, task_id: 7, heartbeat_state: 'not_running'})});
  vi.stubGlobal('fetch', fetcher);
  render(<AgentClaim agents={[{id: 3, name: 'QA', role: 'tester', project_id: 1, execution_status: 'not_implemented'}]} locale="en" />);
  fireEvent.change(screen.getByLabelText('Inspect agent claim'), {target: {value: '3'}});
  expect(await screen.findByText(/Outcome uncertain/)).toBeTruthy();
  expect(screen.getByText(/does not prove an agent/)).toBeTruthy();
  expect(fetcher).toHaveBeenCalledWith('/api/agents/3/claim', undefined);
});
