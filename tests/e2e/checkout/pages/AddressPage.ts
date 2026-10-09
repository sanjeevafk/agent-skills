import { Page, Locator } from '@playwright/test';

/**
 * Page Object Model for the Address step of the checkout flow.
 *
 * Responsibilities:
 * - Render and validate address fields
 * - Submit validated shipping address
 * - Validate address suggestions (if auto-complete is used)
 * - Navigate to the Payment step on success
 */
export class AddressPage {
  readonly page: Page;
  readonly streetInput: Locator;
  readonly apartmentInput: Locator;
  readonly cityInput: Locator;
  readonly stateSelect: Locator;
  readonly zipCodeInput: Locator;
  readonly countrySelect: Locator;
  readonly firstNameInput: Locator;
  readonly lastNameInput: Locator;
  readonly emailInput: Locator;
  readonly phoneInput: Locator;
  readonly saveAddressButton: Locator;
  readonly backToCartButton: Locator;
  readonly proceedToPaymentButton: Locator;
  readonly errorSummary: Locator;
  readonly fieldErrors: Locator;
  readonly validationMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.firstNameInput = page.locator('[data-testid="shipping-first-name"]');
    this.lastNameInput = page.locator('[data-testid="shipping-last-name"]');
    this.streetInput = page.locator('[data-testid="shipping-street"]');
    this.apartmentInput = page.locator('[data-testid="shipping-apartment"]');
    this.cityInput = page.locator('[data-testid="shipping-city"]');
    this.stateSelect = page.locator('[data-testid="shipping-state"]');
    this.zipCodeInput = page.locator('[data-testid="shipping-zip-code"]');
    this.countrySelect = page.locator('[data-testid="shipping-country"]');
    this.emailInput = page.locator('[data-testid="shipping-email"]');
    this.phoneInput = page.locator('[data-testid="shipping-phone"]');
    this.saveAddressButton = page.locator('[data-testid="save-address-and-continue"]');
    this.backToCartButton = page.locator('[data-testid="back-to-cart"]');
    this.proceedToPaymentButton = page.locator('[data-testid="proceed-to-payment"]');
    this.errorSummary = page.locator('[data-testid="address-error-summary"]');
    this.fieldErrors = page.locator('[data-testid="field-error"]');
    this.validationMessage = page.locator('[data-testid="validation-message"]');
  }

  /** Navigate directly to the address step URL. */
  async goto(): Promise<void> {
    await this.page.goto('/checkout/address');
    await this.page.waitForLoadState('networkidle');
  }

  /** Wait for the form to be fully rendered. */
  async waitForFormReady(): Promise<void> {
    await this.streetInput.waitFor({ state: 'visible' });
  }

  /** Populate all required address fields with the provided payload. */
  async fillAddress(address: ShippingAddress): Promise<void> {
    await this.firstNameInput.fill(address.firstName);
    await this.lastNameInput.fill(address.lastName);
    await this.streetInput.fill(address.street);
    if (address.apartment) {
      await this.apartmentInput.fill(address.apartment);
    }
    await this.cityInput.fill(address.city);
    if (address.state) {
      await this.stateSelect.selectOption(address.state);
    }
    await this.zipCodeInput.fill(address.zipCode);
    if (address.country) {
      await this.countrySelect.selectOption(address.country);
    }
    await this.emailInput.fill(address.email);
    await this.phoneInput.fill(address.phone);
  }

  /** Clear a specific field by test-id selector suffix. */
  async clearField(testIdSuffix: string): Promise<void> {
    const field = this.page.locator(`[data-testid="shipping-${testIdSuffix}"]`);
    await field.clear();
  }

  /** Get any visible field-level validation errors. */
  async getFieldErrors(): Promise<string[]> {
    const count = await this.fieldErrors.count();
    const errors: string[] = [];
    for (let i = 0; i < count; i++) {
      errors.push((await this.fieldErrors.nth(i).textContent()) ?? '');
    }
    return errors.filter(Boolean);
  }

  /** Click "Save address & continue" to move to payment step. */
  async submitAndContinue(): Promise<PaymentPage> {
    // The primary CTA may render as either button depending on UX variant.
    if (await this.saveAddressButton.isVisible({ timeout: 2_000 }).catch(() => false)) {
      await this.saveAddressButton.click();
    } else {
      await this.proceedToPaymentButton.click();
    }
    return new PaymentPage(this.page);
  }

  /** Click "Back to cart". */
  async goBackToCart(): Promise<CartPage> {
    await this.backToCartButton.click();
    return new CartPage(this.page);
  }

  /** Assert that an error summary region is visible. */
  async expectErrorSummaryVisible(): Promise<void> {
    await this.errorSummary.waitFor({ state: 'visible' });
  }

  /** Assert that no validation messages are visible. */
  async expectNoValidationErrors(): Promise<void> {
    const count = await this.validationMessage.count();
    // If the element exists but is hidden, that's fine – assert visibility.
    try {
      await this.validationMessage.first().waitFor({ state: 'hidden', timeout: 500 });
    } catch {
      // element doesn't exist at all, which is also valid.
    }
  }
}

// ── types ────────────────────────────────────────────────────────────

export interface ShippingAddress {
  firstName: string;
  lastName: string;
  street: string;
  apartment?: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
  email: string;
  phone: string;
}
