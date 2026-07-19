# ADR 0003: Plugin-based Ranking System

## Problem
In our recommendation pipeline, we needed a way to rank items based on dynamic personalization, budget constraints, nutritional targets, and overall popularity without creating massive, unmaintainable if-else blocks.

## Alternatives Considered
- Monolithic scoring function.
- Machine Learning Learning-to-Rank (LTR) model (e.g., XGBoost).
- Plugin-based architecture.

## Solution
We implemented an `ExplainablePluginRanker` that iterates over a dictionary of `RankingPlugin` objects. Each plugin (e.g., `NutritionScorePlugin`, `BudgetOptimizerPlugin`, `PersonalizationPlugin`) independently evaluates a candidate and returns a `PluginResult` containing a `score`, `weight`, and a human-readable `reason`.

## Why
This architecture provides three major benefits:
1. **Extensibility**: Adding a new scoring factor (e.g., "Seasonal Preference") is as simple as adding a new plugin class.
2. **Explainability**: Because each plugin returns a `reason` (e.g., "High in protein (20g)"), we can trivially expose transparent explanations to the LLM and the frontend.
3. **Simplicity**: It avoids the operational overhead of training and deploying a dedicated LTR model for an MVP, while still achieving highly personalized results.
