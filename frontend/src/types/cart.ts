export type CartItemType = "PRODUCT" | "RECIPE_INGREDIENT" | "MEAL";

export interface CartItem {
  id: string; // The unique ID of the cart item entry
  type: CartItemType;
  name: string;
  image?: string;
  price: number;
  quantity: number;
  nutrition?: {
    protein?: number;
    calories?: number;
  };
  metadata?: Record<string, any>;
}

export interface Cart {
  items: CartItem[];
  // Backend might return more fields like total, but we derive it on the frontend usually
}

export interface CartItemInput {
  type: CartItemType;
  name: string;
  price: number;
  quantity: number;
  image?: string;
  nutrition?: {
    protein?: number;
    calories?: number;
  };
  metadata?: Record<string, any>;
}

export interface CheckoutResult {
  success: boolean;
  orderId?: string;
  message?: string;
}
