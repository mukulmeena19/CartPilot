import { Cart, CartItemInput, CheckoutResult } from "@/types/cart";
import { useStore } from "@/lib/store";

export interface CartService {
  getCart(): Promise<Cart>;
  addItem(item: CartItemInput): Promise<void>;
  removeItem(itemId: string): Promise<void>;
  updateQuantity(itemId: string, quantity: number): Promise<void>;
  clearCart(): Promise<void>;
  checkout(): Promise<CheckoutResult>;
}

export class DemoCartService implements CartService {
  async getCart(): Promise<Cart> {
    return { items: useStore.getState().cartItems };
  }

  async addItem(item: CartItemInput): Promise<void> {
    // In demo mode, we just mutate the Zustand store directly
    const store = useStore.getState();
    const existing = store.cartItems.find(i => i.name === item.name && i.type === item.type);
    
    if (existing) {
      store.updateCartItem(existing.id, { quantity: existing.quantity + item.quantity });
    } else {
      store.addCartItem({
        id: crypto.randomUUID(),
        ...item
      });
    }
  }

  async removeItem(itemId: string): Promise<void> {
    useStore.getState().removeCartItem(itemId);
  }

  async updateQuantity(itemId: string, quantity: number): Promise<void> {
    if (quantity <= 0) {
      await this.removeItem(itemId);
    } else {
      useStore.getState().updateCartItem(itemId, { quantity });
    }
  }

  async clearCart(): Promise<void> {
    useStore.getState().clearCart();
  }

  async checkout(): Promise<CheckoutResult> {
    // Mock processing delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    return { success: true, orderId: "demo-ord-" + Math.floor(Math.random() * 10000) };
  }
}

export class ApiCartService implements CartService {
  private baseUrl = "/api/v1/carts";

  async getCart(): Promise<Cart> {
    const res = await fetch(`${this.baseUrl}/active`);
    if (!res.ok) throw new Error("Failed to fetch cart");
    return res.json();
  }

  async addItem(item: CartItemInput): Promise<void> {
    const res = await fetch(`${this.baseUrl}/items`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(item)
    });
    if (!res.ok) throw new Error("Failed to add item");
  }

  async removeItem(itemId: string): Promise<void> {
    const res = await fetch(`${this.baseUrl}/items/${itemId}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Failed to remove item");
  }

  async updateQuantity(itemId: string, quantity: number): Promise<void> {
    if (quantity <= 0) return this.removeItem(itemId);
    
    const res = await fetch(`${this.baseUrl}/items/${itemId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quantity })
    });
    if (!res.ok) throw new Error("Failed to update item");
  }

  async clearCart(): Promise<void> {
    const res = await fetch(`${this.baseUrl}/clear`, { method: "POST" });
    if (!res.ok) throw new Error("Failed to clear cart");
  }

  async checkout(): Promise<CheckoutResult> {
    const res = await fetch(`/api/v1/orders/checkout`, { method: "POST" });
    if (!res.ok) throw new Error("Checkout failed");
    return res.json();
  }
}

// Factory to resolve the service based on environment
export function getCartService(): CartService {
  if (process.env.NEXT_PUBLIC_DEMO_MODE === "true") {
    return new DemoCartService();
  }
  return new ApiCartService();
}
