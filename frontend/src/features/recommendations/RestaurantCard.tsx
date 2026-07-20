import { Clock, Star, MapPin, CheckCircle2, Navigation, Check, Info } from "lucide-react";
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
          <div className="group relative cursor-help">
            <div className="flex items-center gap-1 bg-foreground text-background px-2 py-0.5 rounded-lg text-sm font-medium">
              <Star className="w-3.5 h-3.5 fill-background" />
              {restaurant.rating}
            </div>
            <div className="absolute bottom-full right-0 mb-2 hidden group-hover:block w-max max-w-[200px] bg-foreground text-background text-xs p-2 rounded shadow-md z-50 whitespace-normal">
              Highly rated by users
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-4 text-secondary text-sm mb-3 flex-wrap">
          <div className="flex items-center gap-1.5">
            <Clock className="w-4 h-4" />
            <span>{restaurant.deliveryTimeMins} mins</span>
          </div>
          <div className="flex items-center gap-1.5">
            <MapPin className="w-4 h-4" />
            <span>Nearby</span>
          </div>
          
          {restaurant.reasons && restaurant.reasons.length > 0 && (
            <div className="group relative cursor-help flex items-center ml-auto">
              <Info className="w-4 h-4 text-muted-foreground hover:text-foreground transition-colors" />
              <div className="absolute bottom-full right-0 mb-2 hidden group-hover:block w-max max-w-[220px] bg-foreground text-background text-xs p-2.5 rounded-lg shadow-xl z-50 whitespace-normal text-left">
                <p className="font-semibold mb-1 opacity-90">Why this matches:</p>
                <ul className="space-y-1">
                  {restaurant.reasons.map((reason, idx) => (
                    <li key={idx} className="flex items-start gap-1.5 leading-tight">
                      <CheckCircle2 className="w-3 h-3 text-primary mt-0.5 shrink-0" />
                      <span>{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
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
      </div>
    </div>
  );
}
