import { Clock, Star, Flame, CheckCircle2, ShoppingBag, Check } from "lucide-react";
import Image from "next/image";
import { useState } from "react";
import { useCart } from "@/hooks/useCart";
import { CartItemInput } from "@/types/cart";

export interface RecipeData {
  id: string;
  title: string;
  rating: number;
  timeMins: number;
  estimatedPrice: number;
  protein: string;
  reasons: string[];
  imageUrl?: string;
  ingredients?: Array<{
    name: string;
    price: number;
    quantity?: number;
    protein?: number;
    calories?: number;
    image_url?: string;
  }>;
}

export function RecipeCard({ recipe }: { recipe: RecipeData }) {
  const { addToCart } = useCart();
  const [isAdded, setIsAdded] = useState(false);

  const handleShopIngredients = () => {
    if (recipe.ingredients && recipe.ingredients.length > 0) {
      recipe.ingredients.forEach(ing => {
        const item: CartItemInput = {
          type: "RECIPE_INGREDIENT",
          name: ing.name,
          price: ing.price,
          quantity: ing.quantity || 1,
          image: ing.image_url,
          nutrition: {
            protein: ing.protein,
            calories: ing.calories,
          }
        };
        addToCart(item);
      });
    } else {
      // Fallback if no ingredients returned
      const fallbackItem: CartItemInput = {
        type: "RECIPE_INGREDIENT",
        name: `${recipe.title} Ingredients Bundle`,
        price: recipe.estimatedPrice,
        quantity: 1,
      };
      addToCart(fallbackItem);
    }
    
    setIsAdded(true);
    setTimeout(() => setIsAdded(false), 2000);
  };

  return (
    <div className="flex flex-col bg-card border border-border rounded-3xl p-4 shadow-sm hover:shadow-md transition-shadow max-w-[300px] gap-3">
      <div className="relative w-full aspect-[4/3] bg-muted rounded-2xl flex items-center justify-center overflow-hidden">
        {recipe.imageUrl ? (
          <Image 
            src={recipe.imageUrl} 
            alt={recipe.title} 
            fill
            className="object-cover"
          />
        ) : (
          <span className="text-4xl">🥗</span>
        )}
      </div>
      
      <div>
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-semibold text-foreground text-lg leading-tight">{recipe.title}</h3>
          <div className="flex items-center gap-1 bg-foreground text-background px-2 py-0.5 rounded-lg text-sm font-medium">
            <Star className="w-3.5 h-3.5 fill-background" />
            {recipe.rating}
          </div>
        </div>
        
        <div className="flex items-center gap-4 text-secondary text-sm mb-3">
          <div className="flex items-center gap-1.5">
            <Clock className="w-4 h-4" />
            <span>{recipe.timeMins}m</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Flame className="w-4 h-4" />
            <span className="text-primary font-medium">{recipe.protein} Protein</span>
          </div>
        </div>
        
        <div className="bg-muted/50 rounded-xl p-3 text-sm">
          <p className="font-medium text-foreground mb-2 text-xs uppercase tracking-wider">Why you'll love this</p>
          <ul className="space-y-1.5">
            {recipe.reasons.map((reason, idx) => (
              <li key={idx} className="flex items-start gap-2 text-secondary">
                <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                <span className="leading-tight">{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
      
      <div className="flex items-center gap-2 mt-1">
        <button className="flex-1 bg-muted text-foreground py-2.5 rounded-xl font-medium hover:bg-border transition-colors">
          View Recipe
        </button>
        <button 
          onClick={handleShopIngredients}
          className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl font-medium transition-colors ${
            isAdded ? "bg-success text-background" : "bg-primary text-primary-foreground hover:bg-primary/90"
          }`}
        >
          {isAdded ? (
            <>
              <Check className="w-4 h-4" /> Added
            </>
          ) : (
            <>
              <ShoppingBag className="w-4 h-4" />
              Shop (₹{recipe.estimatedPrice})
            </>
          )}
        </button>
      </div>
    </div>
  );
}
