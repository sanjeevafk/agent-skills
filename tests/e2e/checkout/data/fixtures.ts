/**
 * Deterministic data fixtures used throughout the checkout E2E suite.
 *
 * Every constant here is stable across runs so that assertions can
 * rely on exact values rather than fuzzy matching.
 */

// ── seeded user identity ─────────────────────────────────────────────

export const TEST_USER = {
  email: 'e2e-checkout@example.com',
  password: 'SecureP@ssw0rd!',
  firstName: 'Jane',
  lastName: 'Doe',
  phone: '+1-555-0147',
};

// Unique per worker via `{REPEAT-EACH}:{WORKER-INDEX}` template tokens
// that Playwright interpolates at runtime.
export function uniqueEmail(repeatEach: number, workerIndex: number): string {
  return `checkout-${repeatEach}-${workerIndex}@e2e.example.com`;
}

export function uniqueOrderSuffix(): string {
  // Millisecond-since-epoch gives us uniqueness within the same worker run.
  return Date.now().toString(36);
}

// ── shipping address ─────────────────────────────────────────────────

export const VALID_SHIPPING_ADDRESS = {
  firstName: 'Jane',
  lastName: 'Doe',
  street: '123 Playwright Lane',
  apartment: 'Apt 4B',
  city: 'San Francisco',
  state: 'CA',
  zipCode: '94102',
  country: 'US',
  email: TEST_USER.email,
  phone: TEST_USER.phone,
};

export const INVALID_ADDRESS = {
  firstName: '',
  lastName: 'Doe',
  street: '',
  city: '',
  state: '',
  zipCode: 'abc',
  country: 'ZZ',
  email: 'not-an-email',
  phone: '123',
};

// ── card details (test-only; never real numbers) ─────────────────────

export const VALID_CARD = {
  number: '4242 4242 4242 4242',
  expiry: '12/30',
  cvc: '123',
  holderName: 'Jane Doe',
};

export const DECLINED_CARD = {
  number: '4000 0000 0000 0002',
  expiry: '12/30',
  cvc: '123',
  holderName: 'Jane Doe',
};

// ── coupon codes ─────────────────────────────────────────────────────

export const COUPONS = {
  VALID: { code: 'E2E10OFF', discountPercent: 10, label: '10% Off' },
  EXPIRED: { code: 'EXPIRED2024', error: 'Coupon has expired' },
  INVALID: { code: 'BADDISCOUNT', error: 'Invalid coupon code' },
} as const;

// ── cart contents (fixture payload) ──────────────────────────────────

export interface CartEntry {
  productId: string;
  name: string;
  price: number;
  quantity: number;
}

export const DEFAULT_CART: CartEntry[] = [
  {
    productId: 'prod-widget-a',
    name: 'Widget A',
    price: 24.99,
    quantity: 2,
  },
  {
    productId: 'prod-gadget-b',
    name: 'Gadget B',
    price: 49.5,
    quantity: 1,
  },
];

export function buildCartTotal(entries: CartEntry[]): number {
  return entries.reduce((sum, e) => sum + e.price * e.quantity, 0);
}

// ── shipping tiers (deterministic mock response) ─────────────────────

export const SHIPPING_TIER = {
  standard: { id: 'ship_std', cost: 5.99, label: 'Standard (5-7 days)', daysMin: 5, daysMax: 7 },
  express: { id: 'ship_exp', cost: 12.5, label: 'Express (2-3 days)', daysMin: 2, daysMax: 3 },
  overnight: { id: 'ship_ont', cost: 24.0, label: 'Overnight', daysMin: 1, daysMax: 1 },
};

export type ShippingTierKey = keyof typeof SHIPPING_TIER;

// ── tax rate ─────────────────────────────────────────────────────────

export const TAX_RATE = 0.0875; // 8.75% CA default

// ── order state machine ──────────────────────────────────────────────

export type OrderStep = 'cart' | 'address' | 'payment' | 'confirmation';

export const ORDER_FLOW_ROUTES: Record<OrderStep, string> = {
  cart: '/cart',
  address: '/checkout/address',
  payment: '/checkout/payment',
  confirmation: '/checkout/confirm',
};
