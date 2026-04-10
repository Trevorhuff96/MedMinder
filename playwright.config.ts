import { existsSync } from 'fs';
import { defineConfig } from '@playwright/test';

const localChromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const launchOptions = existsSync(localChromePath)
  ? { executablePath: localChromePath }
  : undefined;

export default defineConfig({
  testDir: '.',
  testMatch: /.*\.spec\.ts/,
  workers: 1,
  reporter: [
    ['list'],
    [
      './playwright-detailed-reporter.cjs',
      {
        outputDir: 'playwright-report-data',
        markdownFile: 'detailed-report.md',
        jsonFile: 'detailed-report.json',
      },
    ],
  ],
  use: {
    baseURL: 'http://127.0.0.1:8501',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    launchOptions,
  },
  webServer: {
    command: 'PLAYWRIGHT_TEST=1 streamlit run streamlit_app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true',
    url: 'http://127.0.0.1:8501',
    reuseExistingServer: false,
    timeout: 120000,
  },
});
