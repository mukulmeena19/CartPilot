"use client";

import { Message } from "@/lib/store";
import { motion } from "framer-motion";
import { Bot, User } from "lucide-react";
import { ThinkingTimeline } from "./ThinkingTimeline";
import { ProductCard } from "../recommendations/ProductCard";
import { RecipeCard } from "../recommendations/RecipeCard";
import { RestaurantCard } from "../recommendations/RestaurantCard";

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-4 w-full ${isUser ? "justify-end" : "justify-start"}`}
    >
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center border border-primary/30 mt-1">
          <Bot className="w-4 h-4 text-primary" />
        </div>
      )}
      
      <div 
        className={`flex flex-col gap-2 max-w-[85%] ${
          isUser ? "items-end" : "items-start"
        }`}
      >
        <div 
          className={`px-4 py-3 rounded-2xl text-[15px] leading-relaxed ${
            isUser 
              ? "bg-muted text-foreground rounded-tr-sm" 
              : "bg-transparent text-foreground"
          }`}
        >
          {message.content}
        </div>
        
        {message.thinkingSteps && message.thinkingSteps.length > 0 && (
          <div className="mt-2 pl-2 border-l-2 border-border/50">
            <ThinkingTimeline steps={message.thinkingSteps} />
          </div>
        )}
        
        {message.cards && message.cards.length > 0 && (
          <div className="mt-3 flex gap-4 overflow-x-auto pb-4 snap-x snap-mandatory hide-scrollbar">
            {message.cards.map((card, idx) => {
              if (card.type === "product") {
                const productData = {
                  id: card.id,
                  name: card.title,
                  brand: card.brand,
                  price: card.price,
                  matchScore: card.match_score,
                  protein: card.protein,
                  reasons: card.reasons,
                  imageUrl: card.image_url,
                };
                return (
                  <div key={idx} className="snap-center shrink-0">
                    <ProductCard product={productData} />
                  </div>
                );
              }
              if (card.type === "recipe") {
                const recipeData = {
                  id: card.id,
                  title: card.title,
                  rating: card.rating,
                  timeMins: card.time_mins,
                  estimatedPrice: card.estimated_price,
                  protein: card.protein,
                  reasons: card.reasons,
                  imageUrl: card.image_url,
                  ingredients: card.ingredients,
                };
                return (
                  <div key={idx} className="snap-center shrink-0">
                    <RecipeCard recipe={recipeData} />
                  </div>
                );
              }
              if (card.type === "restaurant") {
                const restaurantData = {
                  id: card.id,
                  name: card.title,
                  rating: card.rating,
                  deliveryTimeMins: card.delivery_time_mins,
                  estimatedPrice: card.estimated_price,
                  reasons: card.reasons,
                };
                return (
                  <div key={idx} className="snap-center shrink-0">
                    <RestaurantCard restaurant={restaurantData} />
                  </div>
                );
              }
              return null;
            })}
          </div>
        )}
      </div>
      
      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-muted flex items-center justify-center mt-1">
          <User className="w-4 h-4 text-foreground" />
        </div>
      )}
    </motion.div>
  );
}
