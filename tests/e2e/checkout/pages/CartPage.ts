import { Page, Locator } from '@playwright/test';

/**
 * Page Object Model for the Cart step of the checkout flow.
 *
 * Responsibilities:
 * - Render the list of cart items
 * - Allow quantity adjustments
 * - Validate totals are accurate
 * - Navigate to the Address step
 */
export class CartPage {
  readonly page: Page;
  readonly itemCards: Locator;
  readonly itemQuantityInput: Locator;
  readonly removeItemButton: Locator;
  readonly subtotalDisplay: Locator;
  readonly shippingEstimate: Locator;
  readonly totalDisplay: Locator;
  readonly checkoutButton: Locator;
  readonly emptyCartMessage: Locator;
  readonly couponInput: Locator;
  readonly applyCouponButton: Locator;
  readonly discountBadge: Locator;

  constructor(page: Page) {
    this.page = page;
    this.itemCards = page.locator('[data-testid="cart-item-card"]');
    this.itemQuantityInput = page.locator('[data-testid="item-quantity"]');
    this.removeItemButton = page.locator('[data-testid="remove-item"]');
    this.subtotalDisplay = page.locator('[data-testid="subtotal"]');
    this.shippingEstimate = page.locator('[data-testid="shipping-estimate"]');
    this.totalDisplay = page.locator('[data-testid="cart-total"]');
    this.checkoutButton = page.locator('[data-testid="proceed-to-address"]');
    this.emptyCartMessage = page.locator('[data-testid="empty-cart-message"]');
    this.couponInput = page.locator('[data-testid="coupon-input"]');
    this.applyCouponButton = page.locator('[data-testid="apply-coupon"]');
    this.discountBadge = page.locator('[data-testid="discount-applied"]');
  }

  /** Navigate directly to the cart URL. */
  async goto(): Promise<void> {
    await this.page.goto('/cart');
    // Wait for the meaningful network settle rather than hard timeouts.
    await this.page.waitForLoadState('networkidle');
  }

  /** Wait until at least one cart item card is visible. */
  async waitForItemsLoaded(): Promise<void> {
    await this.itemCards.first().waitFor({ state: 'visible' });
  }

  /** Return the number of distinct line items in the cart. */
  async getItemCount(): Promise<number> {
    return this.itemCards.count();
  }

  /** Return text content of all item cards as structured rows. */
  async getCartItems(): Promise<CartItem[]> {
    const count = await this.itemCards.count();
    const items: CartItem[] = [];
    for (let i = 0; i < count; i++) {
      const card = this.itemCards.nth(i);
      items.push({
        name: await card.locator('[data-testid="item-name"]').textContent(),
        price: parseFloat(
          (await card.locator('[data-testid="item-price"]').textContent())?.replace(/[^0-9.-]+/g, '') ?? '0',
        ),
        quantity: Number(await card.locator('[data-testid="item-quantity"]').inputValue()),
      });
    }
    return items;
  }

  /** Update the quantity for a specific line item (by index). */
  async setQuantity(itemIndex: number, quantity: number): Promise<void> {
    const card = this.itemCards.nth(itemIndex);
    const input = card.locator('[data-testid="item-quantity"]');
    await input.clear();
    await input.fill(String(quantity));
    // The UI should auto-update totals – wait for that signal.
    await this.totalDisplay.waitFor({ state: 'visible' });
  }

  /** Remove a line item by its card index. */
  async removeItem(itemIndex: number): Promise<void> {
    const card = this.itemCards.nth(itemIndex);
    await card.locator('[data-testid="remove-item"]').click();
    // Confirm the card actually left the DOM.
    await this.waitForItemsLoaded();
  }

  /** Apply a coupon code and wait for the discount badge to appear. */
  async applyCoupon(code: string): Promise<void> {
    await this.couponInput.fill(code);
    await this.applyCouponButton.click();
    await this.discountBadge.waitFor({ state: 'visible', timeout: 5_000 });
  }

  /** Get the current total as a number. */
  async getTotal(): Promise<number> {
    const text = await this.totalDisplay.textContent();
    return parseFloat((text ?? '0').replace(/[^0-9.-]+/g, ''));
  }

  /** Click through to the Address step. */
  async proceedToAddress(): Promise<AddressPage> {
    await this.checkoutButton.click();
    // Let the next page assert its own readiness.
    return new AddressPage(this.page);
  }

  /** Assert that the cart is visually empty. */
  async expectEmptyCart(): Promise<void> {
    await this.emptyCartMessage.waitFor({ state: 'visible' });
  }
}

// ── types ────────────────────────────────────────────────────────────

export interface CartItem {
  name: string | null;
  price: number;
  quantity: number;
}
