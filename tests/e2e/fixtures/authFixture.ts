import { test as baseAuth } from '@playwright/test';
import { resolve } from 'path';

/**
 * Path to the serialized auth state file.
 * Each worker gets its own copy so parallel runs don't collide.
 */
const AUTH_STATE_DIR = resolve(__dirname, '../../fixtures/auth-state');

/**
 * `authFixture` — provides an authenticated browser context via
 * `storageState` instead of per-test logins.
 *
 * Workflow:
 * 1. On first run (or when the file is missing), we perform a real
 *    login once and serialize the cookies + localStorage into a JSON
 *    blob stored at `AUTH_STATE_FILE`.
 * 2. All subsequent tests (including retries & other workers) consume
 *    that file directly – zero network calls for authentication.
 *
 * Consumers simply extend this fixture:
 *   import { authFixture } from '../fixtures/auth';
 *   const { authenticatedPage } = authFixture;
 */

interface AuthFixture {
  /** An already-authenticated Page ready for navigation. */
  authenticatedPage: import('@playwright/test').Page;
  /** Forces a fresh login and re-serialises the state file. */
  refreshAuthState: () => Promise<void>;
}

// Lazy singleton – the file is written once per process lifecycle.
let stateFileWritten = false;
const stateFilePath = resolve(AUTH_STATE_DIR, 'state.json');

export const authFixture = baseAuth.extend<AuthFixture>({
  authenticatedPage: async ({ browser }, use) => {
    // --- ensure the state file exists -----------------------------------
    if (!stateFileWritten) {
      const fs = await import('fs');
      const { mkdirSync } = await import('fs');
      mkdirSync(AUTH_STATE_DIR, { recursive: true });

      if (!fs.existsSync(stateFilePath)) {
        console.log('[authFixture] No persisted auth state found – performing initial login…');
        await writeFreshAuthState(browser);
        stateFileWritten = true;
      } else {
        stateFileWritten = true;
      }
    }

    // --- launch a context seeded with the saved state ------------------
    const context = await browser.newContext({
      storageState: stateFilePath,
    });
    const page = await context.newPage();
    await use(page);
    await context.close();
  },

  refreshAuthState: async ({ browser }, use) => {
    await use(async () => {
      stateFileWritten = false; // force re-write on next access
      await writeFreshAuthState(browser);
      stateFileWritten = true;
    });
  },
});

/**
 * Perform a real username/password login against BASE_URL, then persist
 * the resulting cookies and localStorage to disk.
 */
async function writeFreshAuthState(browser: import('@playwright/test').Browser): Promise<void> {
  const baseURL = process.env.BASE_URL ?? 'http://localhost:3000';
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    await page.goto(`${baseURL}/login`);
    await page.waitForLoadState('networkidle');

    // Wait for login form elements.
    await page.locator('[data-testid="login-email"]').waitFor({ state: 'visible' });
    await page.locator('[data-testid="login-password"]').waitFor({ state: 'visible' });

    // Fill and submit credentials.
    await page.locator('[data-testid="login-email"]').fill('e2e-checkout@example.com');
    await page.locator('[data-testid="login-password"]').fill('SecureP@ssw0rd!');
    await page.locator('[data-testid="login-submit"]').click();

    // Wait for post-login redirect / dashboard indicator.
    await page.waitForURL(/\/(checkout|dashboard|account)/, { timeout: 10_000 });

    // Serialize the authenticated state.
    const fs = await import('fs');
    const state = await context.storageState();
    fs.writeFileSync(stateFilePath, JSON.stringify(state, null, 2));
    console.log(`[authFixture] Auth state persisted to ${stateFilePath}`);
  } finally {
    await context.close();
  }
}

export type { AuthFixture };
