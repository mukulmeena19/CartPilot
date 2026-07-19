import { Minus, Plus, Trash2 } from "lucide-react";
import Image from "next/image";
import { CartItem } from "@/types/cart";
import { useCart } from "@/hooks/useCart";

export function CartItemRow({ item }: { item: CartItem }) {
  const { updateQuantity } = useCart();

  const handleDecrease = () => updateQuantity({ id: item.id, quantity: item.quantity - 1 });
  const handleIncrease = () => updateQuantity({ id: item.id, quantity: item.quantity + 1 });
  const handleRemove = () => updateQuantity({ id: item.id, quantity: 0 });

  return (
    <div className="flex gap-4 p-3 bg-muted/30 rounded-2xl border border-border/50 items-center">
      <div className="relative w-16 h-16 bg-muted rounded-xl flex items-center justify-center overflow-hidden shrink-0">
        {item.image ? (
          <Image src={item.image} alt={item.name} fill className="object-cover" />
        ) : (
          <span className="text-xl">{item.type === 'PRODUCT' ? '🛒' : item.type === 'MEAL' ? '🍱' : '🥕'}</span>
        )}
      </div>

      <div className="flex-1 min-w-0">
        <h4 className="font-semibold text-sm truncate" title={item.name}>
          {item.name}
        </h4>
        <div className="text-sm font-bold mt-1">₹{item.price}</div>
      </div>

      <div className="flex items-center gap-2 bg-background border border-border rounded-lg p-1 shrink-0">
        {item.quantity === 1 ? (
          <button 
            onClick={handleRemove}
            className="w-7 h-7 flex items-center justify-center text-destructive hover:bg-destructive/10 rounded-md transition-colors"
            aria-label="Remove item"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        ) : (
          <button 
            onClick={handleDecrease}
            className="w-7 h-7 flex items-center justify-center text-foreground hover:bg-muted rounded-md transition-colors"
            aria-label="Decrease quantity"
          >
            <Minus className="w-4 h-4" />
          </button>
        )}
        
        <span className="w-6 text-center text-sm font-medium tabular-nums" aria-live="polite">
          {item.quantity}
        </span>
        
        <button 
          onClick={handleIncrease}
          className="w-7 h-7 flex items-center justify-center text-foreground hover:bg-muted rounded-md transition-colors"
          aria-label="Increase quantity"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
