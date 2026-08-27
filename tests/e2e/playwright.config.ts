import { defineConfig, devices } from '@playwright/test';
import { resolve } from 'path';

/**
 * Read environment variables with defaults.
 */
const getEnv = (key: string, defaultValue: string): string =>
  process.env[key] ?? defaultValue;

/**
 * Derive worker-scoped tenant prefix from the worker index
 * so that every parallel worker gets its own isolated namespace
 * inside the shared test database.
 */
const workerTenantPrefix = '[worker:{REPEAT-EACH}:{WORKER-INDEX}]';

export default defineConfig({
  // ── test discovery ──────────────────────────────────────────────
  testDir: './checkout',
  // Output directory for per-worker trace / video folders
  outputDir: './test-results',
  // Fully parallel – each worker runs independently
  fullyParallel: true,
  // Fail fast in CI when tests exceed expectations
  forbidOnly: !!process.env.CI,
  // Retries are intentionally set to 0 at the top level; we handle
  // retries at the spec level via quarantine metadata instead so we
  // can gate artifact collection on "this run was a retry".
  retries: 0,
  // Up to 8 concurrent workers; scale down on shared runners.
  workers: process.env.CI ? Number(getEnv('PLAYWRIGHT_WORKERS', '8')) : undefined,
  // Reporters – HTML always, JSON for programmatic consumers
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['json', { outputFile: 'test-results.json' }],
    ['list'],
  ],

  // ── global timeout budget ───────────────────────────────────────
  timeout: 30_000,
  expect: {
    timeout: 10_000,
  },

  // ── use block applied to every test ─────────────────────────────
  use: {
    baseURL: getEnv('BASE_URL', 'http://localhost:3000'),
    actionTimeout: 8_000,
    navigationTimeout: 15_000,
    // Screenshots are captured automatically on failure by the HTML
    // reporter; we do NOT enable page-level screenshots here because
    // they slow down parallel execution and bloat disk.

    // ── video ────────────────────────────────────────────────────
    // Videos are recorded but discarded after each pass.  They are
    // promoted to persistent storage *only* on retry (see the custom
    // `checkoutTest` fixture which checks `info.retry`).
    video: 'retain-on-failure',
    videosPath: resolve(__dirname, 'artifacts/videos'),

    // ── traces ───────────────────────────────────────────────────
    // Traces are also discarded by default. The extended fixture
    // promotes them on retry.
    trace: 'retain-on-failure',
    screenshots: false,
  },

  // ── projects ────────────────────────────────────────────────────
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // ── web server (optional: starts dev server if present) ─────────
  // webServer: {
  //   command: 'npm run dev',
  //   port: 3000,
  //   reuseExistingServer: !process.env.CI,
  // },
});
