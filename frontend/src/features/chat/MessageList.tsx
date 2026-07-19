"use client";

import { useStore } from "@/lib/store";
import { MessageBubble } from "./MessageBubble";
import { useEffect, useRef } from "react";

export function MessageList() {
  const messages = useStore((state) => state.messages);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div 
      ref={scrollRef}
      className="flex flex-col gap-6 p-4 max-w-3xl mx-auto w-full"
    >
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
    </div>
  );
}
