"use client";

import { useState, useRef, useEffect } from "react";
import { ArrowUp, Mic, Square } from "lucide-react";
import { useChatStream } from "@/hooks/useChatStream";

export function ChatInput() {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  const { sendMessage, isStreaming, cancelStream } = useChatStream();

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [text]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!text.trim() || isStreaming) return;
    
    sendMessage(text.trim());
    setText("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <form 
        onSubmit={handleSubmit}
        className="relative flex items-end p-2 bg-card border border-border/50 rounded-3xl shadow-sm focus-within:ring-2 focus-within:ring-primary/20 transition-all"
      >
        <button 
          type="button"
          className="p-3 text-secondary hover:text-foreground transition-colors rounded-full"
        >
          <Mic className="w-5 h-5" />
        </button>
        
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything..."
          className="flex-1 max-h-[200px] bg-transparent border-none focus:ring-0 resize-none py-3 px-2 text-foreground placeholder:text-muted-foreground outline-none"
          rows={1}
        />
        
        {isStreaming ? (
          <button
            type="button"
            onClick={cancelStream}
            className="p-2 m-1 bg-destructive text-destructive-foreground rounded-full hover:opacity-80 transition-opacity"
          >
            <Square className="w-5 h-5 fill-current" />
          </button>
        ) : (
          <button
            type="submit"
            disabled={!text.trim()}
            className="p-2 m-1 bg-foreground text-background rounded-full disabled:opacity-50 hover:opacity-80 transition-opacity"
          >
            <ArrowUp className="w-5 h-5" />
          </button>
        )}
      </form>
      <div className="text-center mt-2">
        <span className="text-[11px] text-muted-foreground font-medium">CartPilot AI can make mistakes. Consider verifying important information.</span>
      </div>
    </div>
  );
}
