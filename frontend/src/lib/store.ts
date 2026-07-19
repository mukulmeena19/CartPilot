import { create } from "zustand";
import { Recommendation } from "@/types/api";
import { CartItem } from "@/types/cart";

export interface ThinkingStep {
  id: string;
  label: string;
  status: "pending" | "active" | "completed";
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  cards?: Recommendation[];
  thinkingSteps?: ThinkingStep[];
}

interface AppState {
  sessionId: string | null;
  userId: number; // Mocked
  messages: Message[];
  isThinking: boolean;
  setSessionId: (id: string) => void;
  addMessage: (msg: Message) => void;
  updateLastMessage: (updates: Partial<Message>) => void;
  appendAssistantChunk: (text: string) => void;
  addOrUpdateThinkingStep: (stepId: string, label: string, status: ThinkingStep["status"]) => void;
  setAssistantCards: (cards: Recommendation[]) => void;
  setIsThinking: (isThinking: boolean) => void;
  clearMessages: () => void;
  
  // Cart Actions
  cartItems: CartItem[];
  addCartItem: (item: CartItem) => void;
  updateCartItem: (id: string, updates: Partial<CartItem>) => void;
  removeCartItem: (id: string) => void;
  clearCart: () => void;
}

export const useStore = create<AppState>((set) => ({
  sessionId: null,
  userId: 1,
  messages: [],
  isThinking: false,
  cartItems: [],

  setSessionId: (id) => set({ sessionId: id }),
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  
  updateLastMessage: (updates) =>
    set((state) => {
      const messages = [...state.messages];
      if (messages.length > 0) {
        const lastIdx = messages.length - 1;
        messages[lastIdx] = { ...messages[lastIdx], ...updates };
      }
      return { messages };
    }),

  appendAssistantChunk: (text) => 
    set((state) => {
      const messages = [...state.messages];
      if (messages.length > 0 && messages[messages.length - 1].role === "assistant") {
        messages[messages.length - 1].content += text;
      }
      return { messages };
    }),

  addOrUpdateThinkingStep: (stepId, label, status) => 
    set((state) => {
      const messages = [...state.messages];
      if (messages.length > 0 && messages[messages.length - 1].role === "assistant") {
        const lastMsg = messages[messages.length - 1];
        const steps = [...(lastMsg.thinkingSteps || [])];
        
        if (status === "active") {
          steps.forEach(s => {
            if (s.status === "active") s.status = "completed";
          });
        }

        const existingIdx = steps.findIndex(s => s.id === stepId);
        if (existingIdx >= 0) {
          steps[existingIdx] = { ...steps[existingIdx], label, status };
        } else {
          steps.push({ id: stepId, label, status });
        }
        
        messages[messages.length - 1].thinkingSteps = steps;
      }
      return { messages };
    }),

  setAssistantCards: (cards) => 
    set((state) => {
      const messages = [...state.messages];
      if (messages.length > 0 && messages[messages.length - 1].role === "assistant") {
        messages[messages.length - 1].cards = cards;
      }
      return { messages };
    }),

  setIsThinking: (isThinking) => set({ isThinking }),
  clearMessages: () => set({ messages: [] }),
  
  // Cart implementations
  addCartItem: (item) => set((state) => ({ cartItems: [...state.cartItems, item] })),
  updateCartItem: (id, updates) => set((state) => ({
    cartItems: state.cartItems.map(i => i.id === id ? { ...i, ...updates } : i)
  })),
  removeCartItem: (id) => set((state) => ({
    cartItems: state.cartItems.filter(i => i.id !== id)
  })),
  clearCart: () => set({ cartItems: [] }),
}));

// Selectors
export const selectCartTotal = (state: AppState) => 
  state.cartItems.reduce((total, item) => total + (item.price * item.quantity), 0);

export const selectCartMacros = (state: AppState) => {
  return state.cartItems.reduce((acc, item) => {
    acc.protein += (item.nutrition?.protein || 0) * item.quantity;
    acc.calories += (item.nutrition?.calories || 0) * item.quantity;
    return acc;
  }, { protein: 0, calories: 0 });
};

