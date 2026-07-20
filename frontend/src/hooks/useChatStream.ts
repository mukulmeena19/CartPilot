import { useState, useCallback, useRef } from "react";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { useStore } from "@/lib/store";
import { StreamEvent } from "@/types/api";

export function useChatStream() {
  const [isStreaming, setIsStreaming] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  
  const { 
    addMessage, 
    appendAssistantChunk, 
    addOrUpdateThinkingStep,
    setAssistantCards,
    updateLastMessage
  } = useStore();

  const cancelStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  const sendMessage = useCallback(async (query: string) => {
    // Cancel any existing stream
    cancelStream();

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    setIsStreaming(true);

    // Add user message
    addMessage({
      id: crypto.randomUUID(),
      role: "user",
      content: query,
      timestamp: new Date().toISOString()
    });

    // Add initial empty assistant message
    const assistantMessageId = crypto.randomUUID();
    addMessage({
      id: assistantMessageId,
      role: "assistant",
      content: "",
      timestamp: new Date().toISOString(),
      thinkingSteps: [],
      cards: []
    });

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      await fetchEventSource(`${baseUrl}/api/v1/conversation/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "text/event-stream",
        },
        body: JSON.stringify({ query }),
        signal: abortController.signal,
        
        onmessage(ev) {
          try {
            const data = JSON.parse(ev.data);
            const eventType = ev.event;
            
            switch(eventType) {
              case "understanding":
              case "planning":
              case "searching":
              case "verifying":
              case "applying":
              case "optimizing":
              case "finalizing":
                addOrUpdateThinkingStep(ev.id || crypto.randomUUID(), data.step, "active");
                
                // Mark previous steps as completed
                const currentSteps = useStore.getState().messages.slice(-1)[0]?.thinkingSteps || [];
                currentSteps.forEach(s => {
                  if (s.status === "active" && s.label !== data.step) {
                    addOrUpdateThinkingStep(s.id, s.label, "completed");
                  }
                });
                break;
                
              case "complete":
                if (data.cart && data.cart.items) {
                   setAssistantCards(data.cart.items);
                }
                if (data.cart && data.cart.explanation && data.cart.explanation.summary) {
                   appendAssistantChunk("\n\n" + data.cart.explanation.summary);
                }
                
                // Clean up any remaining active steps
                const finalSteps = useStore.getState().messages.slice(-1)[0]?.thinkingSteps || [];
                finalSteps.forEach(s => {
                  if (s.status === "active") addOrUpdateThinkingStep(s.id, s.label, "completed");
                });
                break;
                
              case "intent":
              case "workflow":
                addOrUpdateThinkingStep(ev.id || crypto.randomUUID(), `Resolved ${eventType}: ${data.workflow_type || data.intent}`, "completed");
                break;
                
              case "assistant_chunk":
                appendAssistantChunk(data.text);
                break;
                
              case "error":
                appendAssistantChunk(`\n\n**Error:** ${data.message}`);
                break;
                
              case "done":
                // Handled in complete now, but keep for fallback
                break;
            }
          } catch (e) {
            console.error("Error parsing SSE data", e);
          }
        },
        
        onclose() {
          setIsStreaming(false);
        },
        
        onerror(err) {
          console.error("SSE Error:", err);
          setIsStreaming(false);
          // Only throw if we want it to auto-reconnect (we don't)
          throw new Error("Fatal SSE stream error");
        }
      });
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") {
        console.log("Stream aborted by user");
      } else {
        console.error("Stream failed", err);
      }
      setIsStreaming(false);
    }
  }, [addMessage, appendAssistantChunk, addOrUpdateThinkingStep, setAssistantCards, cancelStream]);

  return { sendMessage, isStreaming, cancelStream };
}
