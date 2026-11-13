import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  workers: 1,
  retries: 0,
  timeout: 30_000,
  use: { ...devices['Desktop Chrome'], baseURL: 'http://127.0.0.1:5178', trace: 'off' },
  webServer: [
    {
      command: 'python e2e_server.py', cwd: '../backend',
      url: 'http://127.0.0.1:8018/health/ready', reuseExistingServer: false, timeout: 60_000,
    },
    {
      command: 'npm run dev -- --port 5178 --strictPort',
      env: { AATM_BACKEND_PROXY: 'http://127.0.0.1:8018' },
      url: 'http://127.0.0.1:5178', reuseExistingServer: false, timeout: 60_000,
    },
  ],
});
