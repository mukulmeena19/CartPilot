# ADR 0002: Hybrid Retrieval Strategy

## Problem
Relying solely on vector embeddings for product search often fails on exact keyword matches (e.g., specific brand names or SKUs). Conversely, relying solely on Full-Text Search (FTS) fails on semantic queries (e.g., "healthy snacks for late night").

## Alternatives Considered
- Only Vector Search (pgvector)
- Only FTS (PostgreSQL to_tsvector)
- Dedicated Search Engine (Elasticsearch / Typesense)

## Solution
We chose a Hybrid Retrieval approach natively within PostgreSQL. We query both `pgvector` (cosine similarity) and FTS (`websearch_to_tsquery`) concurrently. We fetch `limit * 2` candidates and calculate a combined score: `(semantic_score * semantic_weight) + (fts_score * fts_weight)`. 

## Why
This avoids the operational complexity of maintaining a separate Elasticsearch cluster while delivering high-quality search results that respect both semantic intent and exact lexical matches. By normalizing the unbounded FTS score via exponential decay, the scores merge predictably.
