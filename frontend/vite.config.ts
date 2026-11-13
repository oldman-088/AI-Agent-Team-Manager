import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const backend = process.env.AATM_BACKEND_PROXY || 'http://127.0.0.1:8001';

export default defineConfig({
  plugins: [react()],
  server: { proxy: { '/health': {target: backend, changeOrigin: false}, '/api': {target: backend, changeOrigin: false} } },
});
