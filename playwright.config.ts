import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  testMatch: /.*\.spec\.ts/,
  workers: 1,
  use: {
    baseURL: 'http://127.0.0.1:8501',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  webServer: {
    command: 'streamlit run streamlit_app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true',
    url: 'http://127.0.0.1:8501',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
