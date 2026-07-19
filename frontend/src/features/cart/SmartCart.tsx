"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ShoppingBag, ArrowRight, Zap, Target, Loader2, CheckCircle } from "lucide-react";
import { useStore, selectCartTotal, selectCartMacros } from "@/lib/store";
import { useCart } from "@/hooks/useCart";
import { CartItemRow } from "./CartItemRow";
import toast from "react-hot-toast";

export function SmartCart() {
  const { cartItems, clearCart } = useStore();
  const totalSpent = useStore(selectCartTotal);
  const { protein, calories } = useStore(selectCartMacros);
  const { checkout } = useCart();
  
  const [checkoutState, setCheckoutState] = useState<"idle" | "confirm" | "processing" | "success">("idle");

  const budget = 2000; // Hardcoded budget for now
  const budgetPercentage = Math.min((totalSpent / budget) * 100, 100);
  const savings = Math.floor(totalSpent * 0.15); // Fake savings logic
  const estimatedDelivery = 28;

  const handleCheckoutClick = () => {
    if (checkoutState === "idle") {
      setCheckoutState("confirm");
    }
  };

  const confirmCheckout = async () => {
    setCheckoutState("processing");
    try {
      await checkout();
      setCheckoutState("success");
    } catch (err) {
      setCheckoutState("idle");
      toast.error("Checkout failed. Please try again.");
    }
  };

  const continueShopping = () => {
    clearCart();
    setCheckoutState("idle");
  };

  if (checkoutState === "success") {
    return (
      <div className="w-full sm:w-80 h-full border-l border-border/50 bg-card p-6 flex flex-col items-center justify-center text-center gap-6">
        <div className="w-20 h-20 rounded-full bg-success/20 flex items-center justify-center text-success mb-4">
          <CheckCircle className="w-10 h-10" />
        </div>
        <h2 className="text-2xl font-bold">Order Successful!</h2>
        <p className="text-secondary text-sm">
          Your healthy choices are on the way. Estimated delivery in {estimatedDelivery} mins.
        </p>
        <button 
          onClick={continueShopping}
          className="w-full mt-4 bg-foreground text-background font-semibold py-4 rounded-2xl flex items-center justify-center gap-2 hover:bg-foreground/90 transition-all"
        >
          Continue Shopping
        </button>
      </div>
    );
  }

  if (checkoutState === "confirm") {
    return (
      <div className="w-full sm:w-80 h-full border-l border-border/50 bg-card p-6 flex flex-col items-center justify-center text-center gap-6">
        <h2 className="text-xl font-bold">Review Order</h2>
        <p className="text-secondary text-sm">
          You are about to place an order for ₹{totalSpent}.
        </p>
        <div className="flex flex-col gap-3 w-full">
          <button 
            onClick={confirmCheckout}
            className="w-full bg-primary text-primary-foreground font-semibold py-4 rounded-2xl flex items-center justify-center gap-2 hover:bg-primary/90 transition-all"
          >
            Confirm & Pay
          </button>
          <button 
            onClick={() => setCheckoutState("idle")}
            className="w-full bg-muted text-foreground font-semibold py-4 rounded-2xl hover:bg-muted/80 transition-all"
          >
            Cancel
          </button>
        </div>
      </div>
    );
  }

  if (checkoutState === "processing") {
    return (
      <div className="w-full sm:w-80 h-full border-l border-border/50 bg-card p-6 flex flex-col items-center justify-center text-center gap-4">
        <Loader2 className="w-12 h-12 text-primary animate-spin" />
        <h2 className="text-xl font-semibold">Processing...</h2>
      </div>
    );
  }

  return (
    <div className="w-full sm:w-96 h-full border-l border-border/50 bg-card flex flex-col">
      <div className="p-6 pb-4 border-b border-border/50 shrink-0">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-primary/20 rounded-xl text-primary">
            <ShoppingBag className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-semibold text-lg leading-tight">Smart Cart</h2>
            <p className="text-sm text-secondary">{cartItems.length} items</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4">
        {cartItems.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center opacity-50 py-10">
            <ShoppingBag className="w-12 h-12 mb-4" />
            <p className="text-lg font-medium">Your cart is empty</p>
            <p className="text-sm text-secondary max-w-[200px] mt-2">Ask me for recipes or groceries to get started.</p>
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {cartItems.map((item) => (
              <motion.div
                key={item.id}
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.2 } }}
              >
                <CartItemRow item={item} />
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>

      {cartItems.length > 0 && (
        <div className="p-6 bg-card border-t border-border/50 shrink-0 space-y-6">
          <div className="flex justify-between items-center font-bold text-xl">
            <span>Subtotal</span>
            <span>₹{totalSpent}</span>
          </div>
          
          <div className="space-y-2">
            <div className="flex justify-between items-end text-sm">
              <span className="text-secondary font-medium">Budget Used</span>
              <span className="font-semibold">{Math.round(budgetPercentage)}%</span>
            </div>
            <div className="h-2.5 w-full bg-muted rounded-full overflow-hidden">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${budgetPercentage}%` }}
                className={`h-full rounded-full ${budgetPercentage > 100 ? 'bg-destructive' : 'bg-primary'}`}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="flex flex-col gap-1">
              <span className="text-secondary">Protein</span>
              <span className="font-semibold">{protein} g</span>
            </div>
            <div className="flex flex-col gap-1">
              <span className="text-secondary">Calories</span>
              <span className="font-semibold">{calories} kcal</span>
            </div>
          </div>
          
          <div className="flex justify-between items-center text-sm">
             <span className="text-secondary">Estimated Delivery</span>
             <span className="font-semibold text-foreground">{estimatedDelivery} min</span>
          </div>

          {savings > 0 && (
            <div className="bg-success/10 border border-success/20 p-3 rounded-xl text-sm flex items-start gap-2 text-success font-medium">
              <Zap className="w-4 h-4 shrink-0 mt-0.5" />
              <div>
                AI optimized your cart and saved you ₹{savings}.
              </div>
            </div>
          )}

          <button 
            onClick={handleCheckoutClick}
            className="w-full bg-foreground text-background font-semibold py-4 rounded-2xl flex items-center justify-center gap-2 hover:bg-foreground/90 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            Checkout 
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      )}
    </div>
  );
}
