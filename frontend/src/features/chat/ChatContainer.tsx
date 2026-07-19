"use client";

import { useStore } from "@/lib/store";
import { ChatInput } from "./ChatInput";
import { MessageList } from "./MessageList";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, ShoppingBag, Utensils, Zap } from "lucide-react";

const SUGGESTIONS = [
  { icon: <Zap className="w-4 h-4 text-warning" />, text: "High Protein Meals" },
  { icon: <ShoppingBag className="w-4 h-4 text-success" />, text: "Weekly Grocery Shopping" },
  { icon: <Utensils className="w-4 h-4 text-destructive" />, text: "Dinner under ₹700" },
  { icon: <Sparkles className="w-4 h-4 text-primary" />, text: "Healthy Breakfast" },
];

export function ChatContainer() {
  const messages = useStore((state) => state.messages);

  return (
    <div className="flex flex-col h-full w-full max-w-4xl mx-auto relative">
      <AnimatePresence mode="wait">
        {messages.length === 0 ? (
          <motion.div 
            key="empty"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex-1 flex flex-col items-center justify-center p-4 mt-[-10vh]"
          >
            <h1 className="text-3xl font-semibold mb-2">CartPilot</h1>
            <p className="text-secondary text-lg mb-8">What can I help you shop today?</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
              {SUGGESTIONS.map((suggestion, idx) => (
                <button 
                  key={idx}
                  className="flex items-center gap-3 p-4 rounded-2xl bg-card border border-border/50 hover:bg-muted transition-colors text-left text-sm font-medium"
                >
                  <div className="p-2 rounded-full bg-background border border-border/50">
                    {suggestion.icon}
                  </div>
                  {suggestion.text}
                </button>
              ))}
            </div>
          </motion.div>
        ) : (
          <motion.div 
            key="chat"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex-1 overflow-y-auto pb-32"
          >
            <MessageList />
          </motion.div>
        )}
      </AnimatePresence>

      <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-background via-background to-transparent pb-8">
        <ChatInput />
      </div>
    </div>
  );
}
