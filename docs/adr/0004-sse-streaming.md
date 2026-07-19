# ADR 0004: Server-Sent Events (SSE) for Conversational UI

## Problem
A core requirement for CartPilot is delivering a highly responsive, "ChatGPT-like" experience where the AI's internal thoughts, retrieved products, and text responses are progressively streamed to the user, rather than waiting for a monolithic, slow response.

## Alternatives Considered
- WebSockets
- GraphQL Subscriptions
- Server-Sent Events (SSE)
- Polling

## Solution
We adopted Server-Sent Events (SSE) using `@microsoft/fetch-event-source` on the frontend and FastAPI's `StreamingResponse` on the backend. The backend `ConversationManager` acts as an async generator that yields structured domain events (e.g., `thinking`, `intent`, `retrieval`, `recommendations`, `assistant_chunk`, `done`).

## Why
SSE is perfectly suited for unidirectional (server-to-client) text streams, which matches the LLM generation paradigm. Unlike WebSockets, SSE works natively over standard HTTP/1.1 or HTTP/2, leverages built-in browser multiplexing, avoids complex stateful connection management, and is much easier to deploy and scale behind standard load balancers and reverse proxies (like NGINX or Railway's edge).
