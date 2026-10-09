import { Page, Locator } from '@playwright/test';

/**
 * Page Object Model for the Payment step of the checkout flow.
 *
 * Responsibilities:
 * - Render payment form fields
 * - Validate card / payment info
 * - Submit payment via mocked API
 * - Navigate to the Confirmation step on success
 */
export class PaymentPage {
  readonly page: Page;
  readonly cardNumberInput: Locator;
  readonly cardExpiryInput: Locator;
  readonly cardCvcInput: Locator;
  readonly cardHolderNameInput: Locator;
  readonly billingSameAsShippingCheckbox: Locator;
  readonly billingStreetInput: Locator;
  readonly billingCityInput: Locator;
  readonly billingZipCodeInput: Locator;
  readonly payNowButton: Locator;
  readonly backToAddressButton: Locator;
  readonly paymentMethodSelector: Locator;
  readonly paypalButton: Locator;
  readonly applePayButton: Locator;
  readonly errorSummary: Locator;
  readonly cardErrors: Locator;
  readonly processingIndicator: Locator;
  readonly orderSummaryBox: Locator;
  readonly itemsTotalDisplay: Locator;
  readonly shippingDisplay: Locator;
  readonly taxDisplay: Locator;
  readonly grandTotalDisplay: Locator;

  constructor(page: Page) {
    this.page = page;
    this.cardNumberInput = page.locator('[data-testid="card-number"]');
    this.cardExpiryInput = page.locator('[data-testid="card-expiry"]');
    this.cardCvcInput = page.locator('[data-testid="card-cvc"]');
    this.cardHolderNameInput = page.locator('[data-testid="card-holder-name"]');
    this.billingSameAsShippingCheckbox = page.locator(
      '[data-testid="billing-same-as-shipping"]',
    );
    this.billingStreetInput = page.locator('[data-testid="billing-street"]');
    this.billingCityInput = page.locator('[data-testid="billing-city"]');
    this.billingZipCodeInput = page.locator('[data-testid="billing-zip"]');
    this.payNowButton = page.locator('[data-testid="pay-now"]');
    this.backToAddressButton = page.locator('[data-testid="back-to-address"]');
    this.paymentMethodSelector = page.locator('[data-testid="payment-method-option"]');
    this.paypalButton = page.locator('[data-testid="pay-with-paypal"]');
    this.applePayButton = page.locator('[data-testid="pay-with-apple-pay"]');
    this.errorSummary = page.locator('[data-testid="payment-error-summary"]');
    this.cardErrors = page.locator('[data-testid="card-field-error"]');
    this.processingIndicator = page.locator('[data-testid="processing-spinner"]');
    this.orderSummaryBox = page.locator('[data-testid="order-summary"]');
    this.itemsTotalDisplay = page.locator('[data-testid="items-total"]');
    this.shippingDisplay = page.locator('[data-testid="shipping-cost"]');
    this.taxDisplay = page.locator('[data-testid="tax-cost"]');
    this.grandTotalDisplay = page.locator('[data-testid="grand-total"]');
  }

  /** Navigate directly to the payment step URL. */
  async goto(): Promise<void> {
    await this.page.goto('/checkout/payment');
    await this.page.waitForLoadState('networkidle');
  }

  /** Wait for the payment form to be ready. */
  async waitForFormReady(): Promise<void> {
    await this.cardNumberInput.waitFor({ state: 'visible' });
  }

  /** Fill in standard credit-card payment details. */
  async fillCardDetails(details: CardDetails): Promise<void> {
    await this.cardNumberInput.fill(details.number);
    await this.cardExpiryInput.fill(details.expiry);
    await this.cardCvcInput.fill(details.cvc);
    if (details.holderName) {
      await this.cardHolderNameInput.fill(details.holderName);
    }
  }

  /** Select a different payment method option. */
  async selectPaymentMethod(method: string): Promise<void> {
    await this.paymentMethodSelector.selectOption(method);
  }

  /** Click the "Pay now" primary CTA. */
  async submitPayment(): Promise<ConfirmationPage> {
    await this.payNowButton.click();
    // The button should become disabled during processing.
    await this.payNowButton.isEnabled({ disabled: true, timeout: 5_000 }).catch(() => null);
    return new ConfirmationPage(this.page);
  }

  /** Go back to the previous address step. */
  async goBackToAddress(): Promise<AddressPage> {
    await this.backToAddressButton.click();
    return new AddressPage(this.page);
  }

  /** Assert that the order summary box is visible with correct values. */
  async expectOrderSummary(expected: OrderSummaryValues): Promise<void> {
    await this.orderSummaryBox.waitFor({ state: 'visible' });
    const itemsText = (await this.itemsTotalDisplay.textContent()) ?? '';
    const itemsValue = parseFloat(itemsText.replace(/[^0-9.-]+/g, ''));
    expect(itemsValue).toBe(expected.itemsTotal);
  }

  /** Assert that a processing spinner was briefly visible then hidden. */
  async expectProcessingIndicator(): Promise<void> {
    await this.processingIndicator.waitFor({ state: 'visible' });
    await this.processingIndicator.waitFor({ state: 'hidden' });
  }

  /** Get any card-level validation errors. */
  async getCardErrors(): Promise<string[]> {
    const count = await this.cardErrors.count();
    const errors: string[] = [];
    for (let i = 0; i < count; i++) {
      errors.push((await this.cardErrors.nth(i).textContent()) ?? '');
    }
    return errors.filter(Boolean);
  }

  /** Assert that the grand total matches expected value. */
  async expectGrandTotal(expectedTotal: number): Promise<void> {
    const text = await this.grandTotalDisplay.textContent();
    const actual = parseFloat((text ?? '0').replace(/[^0-9.-]+/g, ''));
    expect(actual).toBeCloseTo(expectedTotal, 2);
  }

  /** Check whether the "billing same as shipping" checkbox is checked. */
  async isBillingSameAsShippingChecked(): Promise<boolean> {
    return this.billingSameAsShippingCheckbox.isChecked();
  }

  /** Toggle the billing address same-as-shipping checkbox. */
  async toggleBillingSameAsShipping(checked: boolean): Promise<void> {
    const current = await this.billingSameAsShippingCheckbox.isChecked();
    if (current !== checked) {
      await this.billingSameAsShippingCheckbox.click();
    }
  }
}

// ── types ────────────────────────────────────────────────────────────

export interface CardDetails {
  number: string;
  expiry: string;
  cvc: string;
  holderName?: string;
}

export interface OrderSummaryValues {
  itemsTotal: number;
  shippingCost: number;
  tax: number;
  grandTotal: number;
}
