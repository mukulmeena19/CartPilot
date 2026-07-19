"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, Sparkles, AlertCircle, CheckCircle2 } from "lucide-react";
import { generateCartStream, SSEMessage, SSEStage } from "./sse-handler";

const STAGE_MESSAGES: Record<SSEStage, string> = {
  UNDERSTANDING: "Analyzing your request...",
  PLANNING: "Building a shopping plan...",
  RETRIEVAL: "Searching for the best products...",
  VERIFICATION: "Verifying nutritional and brand requirements...",
  MEMORY: "Applying your saved preferences...",
  OPTIMIZATION: "Optimizing the final cart for value...",
  EXPLAINABILITY: "Finalizing recommendations...",
  COMPLETE: "Cart generation complete!",
  ERROR: "An error occurred."
};

export function ChatInterface() {
  const [query, setQuery] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStage, setCurrentStage] = useState<SSEStage | null>(null);
  const [finalCart, setFinalCart] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isProcessing) return;

    setIsProcessing(true);
    setCurrentStage(null);
    setFinalCart(null);
    setError(null);

    await generateCartStream(
      query,
      (msg: SSEMessage) => {
        setCurrentStage(msg.stage);
        if (msg.stage === "COMPLETE") {
          setFinalCart(msg.cart);
        } else if (msg.stage === "ERROR") {
          setError(msg.message || "An unknown error occurred.");
        }
      },
      (err) => {
        setError("Network error connecting to the AI agent.");
        setIsProcessing(false);
      },
      () => {
        setIsProcessing(false);
      }
    );
  };

  return (
    <div className="flex flex-col h-[600px] w-full max-w-4xl mx-auto border border-gray-800 rounded-2xl overflow-hidden bg-gray-950/50 backdrop-blur-xl shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800 bg-gray-900/50">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-indigo-500/10 rounded-lg">
            <Bot className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h2 className="text-sm font-medium text-white">CartPilot Assistant</h2>
            <p className="text-xs text-gray-400">Powered by Agentic AI</p>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        
        {/* Welcome Message */}
        <div className="flex items-start space-x-4">
          <div className="p-2 bg-indigo-500/10 rounded-full shrink-0">
            <Sparkles className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="bg-gray-900 border border-gray-800 rounded-2xl rounded-tl-sm px-5 py-3.5 max-w-[80%] shadow-sm">
            <p className="text-sm text-gray-200 leading-relaxed">
              Hi! I'm your personal shopping agent. Tell me what you need, and I'll orchestrate a complete shopping cart for you. 
              For example: <span className="text-indigo-300 italic">"I need a keto-friendly weekly grocery list under $100."</span>
            </p>
          </div>
        </div>

        {/* User Query Echo */}
        {query && isProcessing && (
          <div className="flex items-start justify-end space-x-4">
            <div className="bg-indigo-600 rounded-2xl rounded-tr-sm px-5 py-3.5 max-w-[80%] shadow-sm">
              <p className="text-sm text-white leading-relaxed">{query}</p>
            </div>
          </div>
        )}

        {/* AI Processing Status */}
        {isProcessing && currentStage && currentStage !== "COMPLETE" && currentStage !== "ERROR" && (
          <div className="flex items-start space-x-4">
            <div className="p-2 bg-indigo-500/10 rounded-full shrink-0">
              <div className="w-5 h-5 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-2xl rounded-tl-sm px-5 py-3.5 shadow-sm">
              <div className="flex flex-col space-y-2">
                <p className="text-sm font-medium text-indigo-400 animate-pulse">
                  {STAGE_MESSAGES[currentStage]}
                </p>
                <div className="flex space-x-1">
                  {Object.keys(STAGE_MESSAGES).slice(0, 7).map((stage, i) => (
                    <div 
                      key={stage} 
                      className={`h-1.5 w-8 rounded-full ${
                        Object.keys(STAGE_MESSAGES).indexOf(currentStage) >= i 
                          ? 'bg-indigo-500' 
                          : 'bg-gray-800'
                      } transition-colors duration-500`}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="flex items-start space-x-4">
            <div className="p-2 bg-red-500/10 rounded-full shrink-0">
              <AlertCircle className="w-5 h-5 text-red-400" />
            </div>
            <div className="bg-red-500/10 border border-red-500/20 rounded-2xl rounded-tl-sm px-5 py-3.5 max-w-[80%]">
              <p className="text-sm text-red-400">{error}</p>
            </div>
          </div>
        )}

        {/* Final Cart Results */}
        {finalCart && (
          <div className="flex items-start space-x-4">
            <div className="p-2 bg-emerald-500/10 rounded-full shrink-0">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-2xl rounded-tl-sm p-5 w-full max-w-[90%] shadow-sm space-y-4">
              <h3 className="text-sm font-semibold text-white">Cart Generated Successfully!</h3>
              
              {/* Display Explainability Summary */}
              {finalCart.explanation && (
                <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-lg">
                  <p className="text-sm text-indigo-200">
                    {finalCart.explanation.summary}
                  </p>
                </div>
              )}

              {/* Display Items */}
              <div className="space-y-3 mt-4">
                {finalCart.items?.map((item: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-950 rounded-lg border border-gray-800">
                    <div className="flex flex-col">
                      <span className="text-sm font-medium text-gray-200">{item.name}</span>
                      {item.brand && <span className="text-xs text-gray-500">{item.brand}</span>}
                    </div>
                    <div className="flex items-center space-x-4">
                      <span className="text-xs px-2 py-1 bg-gray-800 text-gray-300 rounded-full">
                        Qty: {item.quantity}
                      </span>
                      <span className="text-sm font-semibold text-emerald-400">
                        ${item.price?.toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Display Totals */}
              <div className="flex justify-between items-center pt-4 border-t border-gray-800">
                <span className="text-sm text-gray-400">Total Estimated Cost</span>
                <span className="text-lg font-bold text-white">
                  ${finalCart.total_price?.toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-gray-900/80 border-t border-gray-800">
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="E.g., I need ingredients for a lasagna dinner for 4 people..."
            className="w-full bg-gray-950 border border-gray-800 text-white text-sm rounded-full pl-6 pr-14 py-4 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors placeholder:text-gray-600 shadow-inner"
            disabled={isProcessing}
          />
          <button
            type="submit"
            disabled={isProcessing || !query.trim()}
            className="absolute right-2 p-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-800 disabled:text-gray-500 text-white rounded-full transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
