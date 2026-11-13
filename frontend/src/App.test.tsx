// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { App } from './App';

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

describe('dashboard language and data', () => {
  it('switches semantic language and direction and retains user data', async () => {
    const fetcher = vi.fn().mockImplementation(async (url: string) => ({
      ok: true,
      json: async () => url === '/api/projects' ? [{id: 1, name: 'Example مشروع', status: 'active', description: ''}] : [],
    }));
    vi.stubGlobal('fetch', fetcher);
    render(<App />);
    await screen.findAllByText('Example مشروع');
    expect(document.documentElement.lang).toBe('en');
    expect(document.documentElement.dir).toBe('ltr');
    fireEvent.change(screen.getByLabelText('Language'), {target: {value: 'ar'}});
    await waitFor(() => expect(document.documentElement.dir).toBe('rtl'));
    expect(document.documentElement.lang).toBe('ar');
    expect(screen.getByRole('heading', {name: 'المشاريع'})).toBeTruthy();
    expect(screen.getAllByText('Example مشروع').length).toBeGreaterThan(0);
    fireEvent.change(screen.getByLabelText('اللغة'), {target: {value: 'fa'}});
    await waitFor(() => expect(document.documentElement.lang).toBe('fa'));
    expect(document.documentElement.dir).toBe('rtl');
    expect(screen.getByRole('heading', {name: 'پروژه‌ها'})).toBeTruthy();
    fireEvent.change(screen.getByLabelText('زبان'), {target: {value: 'en'}});
    await waitFor(() => expect(document.documentElement.dir).toBe('ltr'));
  });

  it('localizes failure messages when the selected language changes', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation(async (url: string) => ({ok: url === '/health/ready', json: async () => []})));
    render(<App />);
    await screen.findByText(/Could not load data/);
    fireEvent.change(screen.getByLabelText('Language'), {target: {value: 'ar'}});
    expect(screen.getByText(/تعذّر تحميل البيانات/)).toBeTruthy();
  });
});
