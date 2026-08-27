export type ShippingTierKey = 'standard' | 'express' | 'overnight';

export interface ShippingTier {
  id: string;
  cost: number;
  label: string;
  estimatedDaysMin: number;
  estimatedDaysMax: number;
}

export interface APIStubOptions {
  shipping?: {
    standardCost?: number;
    expressCost?: number;
    overnightCost?: number;
    selectedTier?: ShippingTierKey;
  };
  payment?: {
    failWithDecline?: boolean;
  };
  cart?: {
    items?: Array<{
      productId: string;
      name: string;
      price: number;
      quantity: number;
    }>;
    subtotal?: number;
  };
  coupon?: {
    code?: string;
  };
}
