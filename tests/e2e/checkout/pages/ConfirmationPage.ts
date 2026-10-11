import { Page, Locator } from '@playwright/test';

/**
 * Page Object Model for the Confirmation step of the checkout flow.
 *
 * Responsibilities:
 * - Render order confirmation details
 * - Display order number and summary
 * - Allow navigating to order history or home
 */
export class ConfirmationPage {
  readonly page: Page;
  readonly orderNumberDisplay: Locator;
  readonly orderConfirmationMessage: Locator;
  readonly orderSummaryItems: Locator;
  readonly shippingAddressSummary: Locator;
  readonly paymentMethodSummary: Locator;
  readonly orderTotalDisplay: Locator;
  readonly estimatedDeliveryDisplay: Locator;
  readonly trackOrderButton: Locator;
  readonly continueShoppingButton: Locator;
  readonly emailReceiptCheckbox: Locator;
  readonly shareOrderButton: Locator;
  readonly errorBanner: Locator;

  constructor(page: Page) {
    this.page = page;
    this.orderNumberDisplay = page.locator('[data-testid="order-number"]');
    this.orderConfirmationMessage = page.locator(
      '[data-testid="order-confirmation-message"]',
    );
    this.orderSummaryItems = page.locator('[data-testid="order-summary-item"]');
    this.shippingAddressSummary = page.locator('[data-testid="shipping-address-summary"]');
    this.paymentMethodSummary = page.locator('[data-testid="payment-method-summary"]');
    this.orderTotalDisplay = page.locator('[data-testid="order-total"]');
    this.estimatedDeliveryDisplay = page.locator(
      '[data-testid="estimated-delivery-date"]',
    );
    this.trackOrderButton = page.locator('[data-testid="track-order"]');
    this.continueShoppingButton = page.locator('[data-testid="continue-shopping"]');
    this.emailReceiptCheckbox = page.locator('[data-testid="email-receipt-checkbox"]');
    this.shareOrderButton = page.locator('[data-testid="share-order"]');
    this.errorBanner = page.locator('[data-testid="error-banner"]');
  }

  /** Navigate directly to the confirmation URL (deep link). */
  async goto(orderId?: string): Promise<void> {
    const url = orderId ? `/checkout/confirm/${orderId}` : '/checkout/confirm';
    await this.page.goto(url);
    await this.page.waitForLoadState('networkidle');
  }

  /** Wait for the confirmation content to render. */
  async waitForConfirmation(): Promise<void> {
    await this.orderConfirmationMessage.waitFor({ state: 'visible' });
  }

  /** Retrieve the displayed order number. */
  async getOrderNumber(): Promise<string | null> {
    return this.orderNumberDisplay.textContent();
  }

  /** Assert that a specific order number is displayed. */
  async expectOrderNumber(expected: string): Promise<void> {
    const actual = await this.getOrderNumber();
    expect(actual).toContain(expected);
  }

  /** Get the list of ordered items from the confirmation summary. */
  async getOrderedItems(): Promise<OrderItem[]> {
    const count = await this.orderSummaryItems.count();
    const items: OrderItem[] = [];
    for (let i = 0; i < count; i++) {
      const item = this.orderSummaryItems.nth(i);
      items.push({
        name: (await item.locator('[data-testid="ordered-item-name"]').textContent()) ?? '',
        quantity: Number(
          (await item.locator('[data-testid="ordered-item-quantity"]').textContent())?.replace(/\D/g, '') ?? '1',
        ),
        priceEach: parseFloat(
          (await item.locator('[data-testid="ordered-item-price"]').textContent())?.replace(/[^0-9.-]+/g, '') ?? '0',
        ),
      });
    }
    return items;
  }

  /** Get the displayed order total. */
  async getOrderTotal(): Promise<number> {
    const text = await this.orderTotalDisplay.textContent();
    return parseFloat((text ?? '0').replace(/[^0-9.-]+/g, ''));
  }

  /** Get the estimated delivery date string. */
  async getEstimatedDelivery(): Promise<string | null> {
    return this.estimatedDeliveryDisplay.textContent();
  }

  /** Click "Continue shopping" – returns CartPage. */
  async continueShopping(): Promise<CartPage> {
    await this.continueShoppingButton.click();
    return new CartPage(this.page);
  }

  /** Click "Track order" – returns a page reference. */
  async trackOrder(): Promise<ConfirmationPage> {
    await this.trackOrderButton.click();
    // Stay on the same page object since track-order may be a modal/drawer.
    return this;
  }

  /** Assert that no error banner is visible. */
  async expectNoErrors(): Promise<void> {
    const visible = await this.errorBanner.isVisible({ timeout: 1_000 }).catch(() => false);
    expect(visible).toBe(false);
  }
}

// ── types ────────────────────────────────────────────────────────────

export interface OrderItem {
  name: string;
  quantity: number;
  priceEach: number;
}
