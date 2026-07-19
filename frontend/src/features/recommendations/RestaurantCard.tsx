import { Clock, Star, MapPin, CheckCircle2, Navigation, Check } from "lucide-react";
import { useState } from "react";
import { useCart } from "@/hooks/useCart";
import { CartItemInput } from "@/types/cart";

export interface RestaurantData {
  id: string;
  name: string;
  rating: number;
  deliveryTimeMins: number;
  estimatedPrice: number;
  reasons: string[];
}

export function RestaurantCard({ restaurant }: { restaurant: RestaurantData }) {
  const { addToCart } = useCart();
  const [isAdded, setIsAdded] = useState(false);

  const handleAddMeal = () => {
    const item: CartItemInput = {
      type: "MEAL",
      name: `${restaurant.name} Meal`,
      price: restaurant.estimatedPrice,
      quantity: 1,
    };
    
    addToCart(item);
    
    setIsAdded(true);
    setTimeout(() => setIsAdded(false), 2000);
  };

  return (
    <div className="flex flex-col bg-card border border-border rounded-3xl p-4 shadow-sm hover:shadow-md transition-shadow max-w-[300px] gap-3 h-full">
      <div className="relative w-full h-32 bg-muted rounded-2xl flex items-center justify-center overflow-hidden">
        <span className="text-4xl">🏪</span>
      </div>
      
      <div className="flex-1">
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-semibold text-foreground text-lg leading-tight">{restaurant.name}</h3>
          <div className="flex items-center gap-1 bg-foreground text-background px-2 py-0.5 rounded-lg text-sm font-medium">
            <Star className="w-3.5 h-3.5 fill-background" />
            {restaurant.rating}
          </div>
        </div>
        
        <div className="flex items-center gap-4 text-secondary text-sm mb-3">
          <div className="flex items-center gap-1.5">
            <Clock className="w-4 h-4" />
            <span>{restaurant.deliveryTimeMins} mins</span>
          </div>
          <div className="flex items-center gap-1.5">
            <MapPin className="w-4 h-4" />
            <span>Nearby</span>
          </div>
        </div>
        
        <div className="bg-muted/50 rounded-xl p-3 text-sm">
          <p className="font-medium text-foreground mb-2 text-xs uppercase tracking-wider">Perfect match because</p>
          <ul className="space-y-1.5">
            {restaurant.reasons.map((reason, idx) => (
              <li key={idx} className="flex items-start gap-2 text-secondary">
                <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                <span className="leading-tight">{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
      
      <div className="flex items-center gap-2 mt-auto pt-2">
        <button 
          onClick={handleAddMeal}
          className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl font-medium transition-colors ${
            isAdded ? "bg-success text-background" : "bg-primary text-primary-foreground hover:bg-primary/90"
          }`}
        >
          {isAdded ? (
            <>
              <Check className="w-4 h-4" /> Added
            </>
          ) : (
            <>
              Add Meal
            </>
          )}
        </button>
        <button className="p-2.5 bg-muted text-foreground rounded-xl hover:bg-border transition-colors">
          <Navigation className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
