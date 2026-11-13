// @vitest-environment jsdom
import { afterEach, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { TaskDetails } from './TaskDetails';
import type { Task } from './tasks';

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

it('shows blockers outside the loaded page, filters choices and handles rejection', async () => {
  const tasks: Task[] = [
    {id: 1, project_id: 1, title: 'One', description: '', status: 'pending'},
    {id: 2, project_id: 1, title: 'Two', description: '', status: 'pending'},
    {id: 3, project_id: 2, title: 'Other project', description: '', status: 'pending'},
  ];
  vi.stubGlobal('fetch', vi.fn().mockImplementation(async (url: string, init?: RequestInit) => {
    if (init?.method) return {ok: false};
    return {ok: true, json: async () => url.endsWith('/readiness')
      ? {task_id: 1, status: 'pending', ready: false, blocking_dependencies: [99]}
      : [99]};
  }));
  render(<TaskDetails task={tasks[0]} tasks={tasks} locale="en" onChanged={async () => {}} />);
  await screen.findByText(/Incomplete prerequisites:/);
  expect(screen.getAllByText(/Task ID #99/).length).toBeGreaterThan(0);
  expect(screen.queryByRole('option', {name: /Other project/})).toBeNull();
  fireEvent.change(screen.getByLabelText('Prerequisite'), {target: {value: '2'}});
  fireEvent.click(screen.getByRole('button', {name: 'Add dependency'}));
  await waitFor(() => expect(screen.getByRole('alert').textContent).toContain('Could not load or change dependencies'));
});
