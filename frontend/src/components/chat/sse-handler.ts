import { api } from "@/lib/api";

export type SSEStage = 
  | "UNDERSTANDING"
  | "PLANNING"
  | "RETRIEVAL"
  | "VERIFICATION"
  | "MEMORY"
  | "OPTIMIZATION"
  | "EXPLAINABILITY"
  | "COMPLETE"
  | "ERROR";

export interface SSEMessage {
  stage: SSEStage;
  cart?: any;
  message?: string;
}

export const generateCartStream = async (
  query: string, 
  onMessage: (msg: SSEMessage) => void,
  onError: (err: any) => void,
  onComplete: () => void
) => {
  try {
    // Note: EventSource doesn't allow sending a JSON body in a POST request easily.
    // Instead, we can use the fetch API to process the SSE stream manually.
    const url = `${api.defaults.baseURL}/shopping/generate-cart`;
    
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("token")}`
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error("Failed to connect to AI stream");
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder("utf-8");

    if (!reader) {
      throw new Error("No reader available");
    }

    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      
      const lines = buffer.split("\n");
      buffer = lines.pop() || ""; // Keep the last incomplete line in the buffer

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const dataStr = line.substring(6); // Remove "data: "
            const data = JSON.parse(dataStr) as SSEMessage;
            onMessage(data);
            
            if (data.stage === "COMPLETE" || data.stage === "ERROR") {
              onComplete();
            }
          } catch (e) {
            console.error("Error parsing SSE message:", e);
          }
        }
      }
    }
    
    onComplete();
  } catch (error) {
    onError(error);
  }
};
