import { CheckCircle2, ShoppingCart, Info, Star, Check } from "lucide-react";
import Image from "next/image";
import { useState } from "react";
import { useCart } from "@/hooks/useCart";
import { CartItemInput } from "@/types/cart";

export interface ProductData {
  id: string;
  name: string;
  brand?: string;
  price: number;
  matchScore: number;
  protein?: string;
  reasons: string[];
  imageUrl?: string;
}

export function ProductCard({ product }: { product: ProductData }) {
  const { addToCart } = useCart();
  const [isAdded, setIsAdded] = useState(false);

  const handleAdd = () => {
    const item: CartItemInput = {
      type: "PRODUCT",
      name: product.name,
      price: product.price,
      quantity: 1,
      image: product.imageUrl,
      nutrition: {
        protein: product.protein ? parseFloat(product.protein) : undefined,
      }
    };
    
    addToCart(item);
    
    setIsAdded(true);
    setTimeout(() => setIsAdded(false), 2000);
  };

  return (
    <div className="flex flex-col bg-card border border-border rounded-3xl p-4 shadow-sm hover:shadow-md transition-shadow max-w-[300px] gap-3">
      <div className="relative w-full aspect-square bg-muted rounded-2xl flex items-center justify-center overflow-hidden">
        {product.imageUrl ? (
          <Image 
            src={product.imageUrl} 
            alt={product.name} 
            fill
            className="object-cover"
          />
        ) : (
          <span className="text-4xl">🥛</span>
        )}
      </div>
      
      <div className="flex-1 flex flex-col justify-between">
        <div>
          <div className="flex justify-between items-start mb-1">
            <h3 className="font-semibold text-foreground text-lg leading-tight">{product.brand ? `${product.brand} ` : ''}{product.name}</h3>
          </div>
          
          <div className="flex items-center gap-1 text-warning mb-2 group relative w-fit cursor-help">
            {Array.from({ length: 5 }).map((_, i) => (
              <Star key={i} className={`w-4 h-4 ${i < Math.round(product.matchScore / 20) ? "fill-warning" : "text-muted"}`} />
            ))}
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-max max-w-[200px] bg-foreground text-background text-xs p-2 rounded shadow-md z-50 whitespace-normal">
              Based on {product.matchScore}% preference match
            </div>
          </div>
          
          <div className="flex items-center justify-between mt-2 flex-wrap gap-2">
            <span className="text-lg font-bold text-foreground">₹{product.price}</span>
            <div className="flex items-center gap-2">
              {product.protein && (
                <div className="group relative cursor-help">
                  <span className="text-xs font-medium px-2 py-1 bg-primary/10 text-primary rounded-full">
                    {product.protein} Protein
                  </span>
                  <div className="absolute bottom-full right-0 mb-2 hidden group-hover:block w-max max-w-[200px] bg-foreground text-background text-xs p-2 rounded shadow-md z-50 whitespace-normal text-left">
                    High protein pick based on your goals
                  </div>
                </div>
              )}
              
              {product.reasons && product.reasons.length > 0 && (
                <div className="group relative cursor-help flex items-center">
                  <Info className="w-4 h-4 text-muted-foreground hover:text-foreground transition-colors" />
                  <div className="absolute bottom-full right-0 mb-2 hidden group-hover:block w-max max-w-[220px] bg-foreground text-background text-xs p-2.5 rounded-lg shadow-xl z-50 whitespace-normal text-left">
                    <p className="font-semibold mb-1 opacity-90">Why this was chosen:</p>
                    <ul className="space-y-1">
                      {product.reasons.map((reason, idx) => (
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
        </div>
      </div>
      
      <div className="flex items-center gap-2 mt-2">
        <button 
          onClick={handleAdd}
          className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl font-medium transition-colors ${
            isAdded ? "bg-success text-background" : "bg-foreground text-background hover:bg-foreground/90"
          }`}
        >
          {isAdded ? (
            <>
              <Check className="w-4 h-4" /> Added!
            </>
          ) : (
            <>
              <ShoppingCart className="w-4 h-4" /> Add
            </>
          )}
        </button>
      </div>
    </div>
  );
}
