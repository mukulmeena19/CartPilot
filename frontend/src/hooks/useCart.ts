import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getCartService } from "@/lib/services/CartService";
import { CartItemInput } from "@/types/cart";
import { useStore } from "@/lib/store";
import toast from "react-hot-toast";

const cartService = getCartService();

export function useCart() {
  const queryClient = useQueryClient();

  const { data: cart, isLoading } = useQuery({
    queryKey: ["cart"],
    queryFn: () => cartService.getCart(),
    // In demo mode, since cart is in Zustand, we might just rely on Zustand directly.
    // But for API mode, this fetches the real cart.
  });

  const addToCartMutation = useMutation({
    mutationFn: (item: CartItemInput) => cartService.addItem(item),
    onMutate: async (newItem) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ["cart"] });
      
      const previousCart = queryClient.getQueryData(["cart"]);
      
      // Update store optimistically
      const store = useStore.getState();
      const existing = store.cartItems.find(i => i.name === newItem.name && i.type === newItem.type);
      if (existing) {
        store.updateCartItem(existing.id, { quantity: existing.quantity + newItem.quantity });
      } else {
        store.addCartItem({ id: crypto.randomUUID(), ...newItem });
      }

      return { previousCart };
    },
    onError: (err, newItem, context) => {
      toast.error("Couldn't add item. Please try again.");
      if (context?.previousCart) {
        queryClient.setQueryData(["cart"], context.previousCart);
      }
      // Depending on if we rely purely on Zustand for the view, 
      // we might need to rollback the store here if in API mode.
      // But Demo mode is pure Zustand. Let's keep it simple: refetch on error.
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["cart"] });
    },
  });

  const updateQuantityMutation = useMutation({
    mutationFn: ({ id, quantity }: { id: string; quantity: number }) => cartService.updateQuantity(id, quantity),
    onMutate: async ({ id, quantity }) => {
      await queryClient.cancelQueries({ queryKey: ["cart"] });
      const previousCart = queryClient.getQueryData(["cart"]);
      
      const store = useStore.getState();
      if (quantity <= 0) {
        store.removeCartItem(id);
      } else {
        store.updateCartItem(id, { quantity });
      }

      return { previousCart };
    },
    onError: (err, variables, context) => {
      toast.error("Couldn't update cart.");
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["cart"] });
    },
  });

  const checkoutMutation = useMutation({
    mutationFn: () => cartService.checkout(),
  });

  return {
    cart,
    isLoading,
    addToCart: addToCartMutation.mutate,
    updateQuantity: updateQuantityMutation.mutate,
    checkout: checkoutMutation.mutateAsync,
    isAdding: addToCartMutation.isPending,
  };
}
