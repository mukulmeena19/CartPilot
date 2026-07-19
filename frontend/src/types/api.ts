export type RecommendationType = "product" | "recipe" | "restaurant";

export interface BaseRecommendation {
  id: string;
  type: RecommendationType;
  title: string;
  reasons: string[];
}

export interface ProductRecommendation extends BaseRecommendation {
  type: "product";
  brand?: string;
  price: number;
  match_score: number;
  protein?: string;
  image_url?: string;
}

export interface RecipeRecommendation extends BaseRecommendation {
  type: "recipe";
  rating: number;
  time_mins: number;
  estimated_price: number;
  protein: string;
  image_url?: string;
  ingredients?: Array<{
    name: string;
    price: number;
    quantity?: number;
    protein?: number;
    calories?: number;
    image_url?: string;
  }>;
}

export interface RestaurantRecommendation extends BaseRecommendation {
  type: "restaurant";
  rating: number;
  delivery_time_mins: number;
  estimated_price: number;
}

export type Recommendation = ProductRecommendation | RecipeRecommendation | RestaurantRecommendation;

export type StreamEventType = 
  | "connected"
  | "thinking"
  | "intent"
  | "workflow"
  | "retrieval"
  | "ranking"
  | "recommendations"
  | "cart_update"
  | "assistant_chunk"
  | "done"
  | "error";

export interface StreamEvent<T = any> {
  id: string;
  timestamp: string;
  event: StreamEventType;
  data: T;
}
