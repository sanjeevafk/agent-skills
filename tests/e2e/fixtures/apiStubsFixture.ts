import { test as baseApi } from '@playwright/test';
import type { APIStubOptions, ShippingTierKey } from './types';

/**
 * `apiStubsFixture` — intercepts outbound network calls for shipping
 * and payment endpoints so that every test runs against deterministic,
 * in-memory responses.
 *
 * By default we stub:
 *   POST /api/shipping/rates     → returns a fixed tier list
 *   POST /api/payments/process   → succeeds or declines based on card prefix
 *   GET  /api/cart               → returns the fixture cart payload
 *   PUT  /api/cart/quantity/:id  → echoes the new quantity
 *   POST /api/coupons/apply      → resolves based on the coupon code
 *
 * Tests may extend or disable individual stubs via the `stubAPI`
 * fixture parameter.
 */

interface APIMocks {
  /** Call once per test to install all route interceptors on the page's browser context. */
  interceptShippingRates: (overrides?: Partial<APIStubOptions['shipping']>) => void;
  /** Call once per test to install the payment processing interceptor. */
  interceptPaymentProcess: (failWithDecline: boolean) => void;
  /** Call once per test to install the cart-data interceptor. */
  interceptCartData: () => void;
  /** Call once per test to install the coupon-apply interceptor. */
  interceptCouponApply: () => void;
}

export const apiStubsFixture = baseApi.extend<{
  interceptShippingRates: (opts?: Partial<APIStubOptions['shipping']>) => void;
  interceptPaymentProcess: (fail: boolean) => void;
  interceptCartData: () => void;
  interceptCouponApply: () => void;
}>({
  interceptShippingRates: async ({}, use, workerInfo) => {
    // We install stubs lazily inside each test body via the callback,
    // not in the fixture setup, so that multiple tests in the same file
    // can call it independently.
    await use((overrides: Partial<APIStubOptions['shipping']> = {}) => {
      // Stubbing is performed at test time when `page` and `context` are available.
      // This getter exposes a closure that captures the current test's context.
      return installShippingStub(overrides);
    });
  },

  interceptPaymentProcess: async ({}, use) => {
    await use((fail: boolean) => {
      return installPaymentStub(fail);
    });
  },

  interceptCartData: async ({}, use) => {
    await use(() => {
      return installCartStub();
    });
  },

  interceptCouponApply: async ({}, use) => {
    await use(() => {
      return installCouponStub();
    });
  },
});

// --- helper functions that close over the current test's context ------

let currentPage: import('@playwright/test').Page | null = null;
let currentContext: import('@playwright/test').BrowserContext | null = null;

/**
 * These are called inside individual tests after the page/context has been
 * provided by an outer fixture chain. They register route handlers once
 * per test and clean them up automatically when the request completes.
 */

export function bindContext(page: import('@playwright/test').Page, ctx: import('@playwright/test').BrowserContext): void {
  currentPage = page;
  currentContext = ctx;
}

function getMustHaveContext(): import('@playwright/test').BrowserContext {
  if (!currentContext) {
    throw new Error(
      '[apiStubsFixture] BrowserContext not bound. Ensure bindContext() is called before installing stubs.',
    );
  }
  return currentContext;
}

function installShippingStub(overrides: Partial<APIStubOptions['shipping']> = {}) {
  const ctx = getMustHaveContext();
  const tierMap = {
    standard: { id: 'ship_std', cost: overrides.standardCost ?? 5.99, label: 'Standard (5-7 days)', estimatedDaysMin: 5, estimatedDaysMax: 7 },
    express: { id: 'ship_exp', cost: overrides.expressCost ?? 12.50, label: 'Express (2-3 days)', estimatedDaysMin: 2, estimatedDaysMax: 3 },
    overnight: { id: 'ship_ont', cost: overrides.overnightCost ?? 24.00, label: 'Overnight', estimatedDaysMin: 1, estimatedDaysMax: 1 },
  };

  ctx.route('**/api/shipping/rates', async (route) => {
    if (route.request().method() !== 'POST') {
      return route.fallback();
    }
    const tier = (overrides.selectedTier as ShippingTierKey) ?? 'standard';
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ tier: tierMap[tier], cost: tierMap[tier].cost }),
    });
  });
}

function installPaymentStub(fail: boolean) {
  const ctx = getMustHaveContext();
  ctx.route('**/api/payments/process', async (route) => {
    if (route.request().method() !== 'POST') {
      return route.fallback();
    }
    const body = await route.request().json() as Record<string, unknown>;
    const cardNumber = (body.cardNumber as string)?.replace(/\s/g, '') ?? '';

    if (fail || cardNumber.startsWith('4000')) {
      await route.fulfill({
        status: 402,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Payment declined', code: 'CARD_DECLINED' }),
      });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        transactionId: `txn_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
        lastFour: cardNumber.slice(-4),
      }),
    });
  });
}

function installCartStub() {
  const ctx = getMustHaveContext();
  ctx.route('**/api/cart', async (route) => {
    if (route.request().method() !== 'GET') {
      return route.fallback();
    }
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [
          { productId: 'prod-widget-a', name: 'Widget A', price: 24.99, quantity: 2 },
          { productId: 'prod-gadget-b', name: 'Gadget B', price: 49.5, quantity: 1 },
        ],
        subtotal: 99.48,
      }),
    });
  });
}

function installCouponStub() {
  const ctx = getMustHaveContext();
  ctx.route('**/api/coupons/apply', async (route) => {
    if (route.request().method() !== 'POST') {
      return route.fallback();
    }
    const body = await route.request().json() as Record<string, unknown>;
    const code = (body.code as string)?.toUpperCase() ?? '';

    const validCodes: Record<string, { discountPercent: number; label: string }> = {
      E2E10OFF: { discountPercent: 10, label: '10% Off' },
      SAVE20: { discountPercent: 20, label: '$20 Off' },
    };

    if (code === 'EXPIRED2024') {
      await route.fulfill({
        status: 410,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Coupon has expired' }),
      });
      return;
    }

    if (!validCodes[code]) {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Invalid coupon code' }),
      });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        valid: true,
        ...validCodes[code],
        amountOff: validCodes[code].discountPercent,
      }),
    });
  });
}
