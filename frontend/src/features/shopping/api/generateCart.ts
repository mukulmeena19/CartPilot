import { fetchEventSource } from '@microsoft/fetch-event-source';
import { PipelineStage } from '../types';

interface GenerateCartOptions {
  query: string;
  token?: string; // JWT token if needed
  onProgress: (stage: PipelineStage) => void;
  onComplete: (cart: any) => void;
  onError: (error: any) => void;
}

export const generateCartStream = async ({ query, token, onProgress, onComplete, onError }: GenerateCartOptions) => {
  const url = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/shopping/generate-cart`;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'Accept': 'text/event-stream',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    await fetchEventSource(url, {
      method: 'POST',
      headers,
      body: JSON.stringify({ query }),
      async onopen(response) {
        if (response.ok) {
          return; // everything's good
        } else if (response.status >= 400 && response.status < 500 && response.status !== 429) {
          // client-side errors are usually non-retriable
          throw new Error(`Failed to generate cart: ${response.status}`);
        } else {
          throw new Error(`Failed to connect: ${response.status}`);
        }
      },
      onmessage(msg) {
        // Assume backend sends: data: {"stage": "PLANNING", ...}
        if (msg.event === 'FatalError') {
          throw new Error(msg.data);
        }
        
        try {
          const payload = JSON.parse(msg.data);
          
          if (payload.stage === 'ERROR') {
             throw new Error(payload.message || 'Pipeline error occurred');
          }
          
          if (payload.stage === 'COMPLETE') {
             onComplete(payload.cart);
          } else {
             onProgress(payload.stage as PipelineStage);
          }
        } catch (e) {
          // Ignore parsing errors for non-JSON events like ping
        }
      },
      onclose() {
        // SSE closed by server
      },
      onerror(err) {
        onError(err);
        throw err; // throw to stop retrying
      }
    });
  } catch (error) {
    onError(error);
  }
};
