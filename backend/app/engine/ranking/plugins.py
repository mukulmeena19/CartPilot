"""
Plugin-based Ranking Engine.
Computes the final score for retrieved items using multiple signals.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from app.engine.models import CandidateScore, PluginResult

logger = logging.getLogger(__name__)


class RankingPlugin(ABC):
    """Abstract base class for all ranking plugins."""
    
    @abstractmethod
    def score(self, candidate: CandidateScore, context: Dict[str, Any]) -> PluginResult:
        """Return a PluginResult containing score, weight, and reason."""
        pass


class NutritionScorePlugin(RankingPlugin):
    def score(self, candidate: CandidateScore, context: Dict[str, Any]) -> PluginResult:
        item = candidate.item
        protein_target = context.get("protein_target")
        
        if protein_target and hasattr(item, "nutrition") and item.nutrition:
            protein = item.nutrition.get("protein", 0.0)
            if protein >= protein_target:
                return PluginResult(score=1.0, reason=f"High in protein ({protein}g)", weight=1.0)
            elif protein >= protein_target / 2:
                return PluginResult(score=0.5, reason=f"Good source of protein", weight=1.0)
                
        return PluginResult(score=0.0, weight=1.0)


class BudgetOptimizerPlugin(RankingPlugin):
    def score(self, candidate: CandidateScore, context: Dict[str, Any]) -> PluginResult:
        item = candidate.item
        target_budget = context.get("target_budget")
        
        if target_budget and hasattr(item, "price"):
            price = item.price
            if price <= target_budget * 0.5:
                return PluginResult(score=1.0, reason="Great value (well under budget)", weight=1.0)
            elif price <= target_budget:
                return PluginResult(score=0.7, reason="Within your budget", weight=1.0)
                
        return PluginResult(score=0.0, weight=1.0)


class PopularityScorePlugin(RankingPlugin):
    def score(self, candidate: CandidateScore, context: Dict[str, Any]) -> PluginResult:
        item = candidate.item
        # Simulate popularity (e.g. from a rating or purchase count)
        rating = getattr(item, "rating", 4.0)
        # Normalize rating from 1-5 to 0-1
        norm_rating = max(0.0, min(1.0, (rating - 1) / 4.0))
        
        if norm_rating >= 0.8:
            return PluginResult(score=norm_rating, reason="Highly rated by customers", weight=0.5)
        return PluginResult(score=norm_rating, weight=0.5)


class ExplainablePluginRanker:
    def __init__(self, plugins: Dict[str, RankingPlugin], weights: Dict[str, float] = None):
        self.plugins = plugins
        self.global_weights = weights or {}

    def rank(self, candidates: List[CandidateScore], context: Dict[str, Any]) -> List[CandidateScore]:
        """
        Ranks items by applying all plugins and aggregating reasons.
        """
        for c in candidates:
            total_plugin_score = 0.0
            total_plugin_weight = 0.0
            
            for name, plugin in self.plugins.items():
                try:
                    res = plugin.score(c, context)
                    # Override weight if specified globally
                    global_w = self.global_weights.get(name, res.weight)
                    
                    c.plugin_results[name] = res
                    
                    total_plugin_score += res.score * global_w
                    total_plugin_weight += global_w
                    
                    if res.reason and res.score > 0.5:
                        c.reasons.append(res.reason)
                        
                except Exception as e:
                    logger.error(f"Plugin {name} failed for item {c.candidate_id}: {e}")
            
            # Incorporate plugin scores into final score
            # We can treat the base retrieval score (final_score so far) as another signal
            normalized_plugin_score = total_plugin_score / total_plugin_weight if total_plugin_weight > 0 else 0.0
            
            # Simple weighting: 50% retrieval + 50% plugin ranking
            c.final_score = (c.final_score * 0.5) + (normalized_plugin_score * 0.5)
            
            # Also store explicit plugin scores for logging
            c.nutrition_score = c.plugin_results.get("nutrition", PluginResult(score=0)).score
            c.budget_score = c.plugin_results.get("budget", PluginResult(score=0)).score
            c.popularity_score = c.plugin_results.get("popularity", PluginResult(score=0)).score
            
        # Sort by updated final score
        sorted_cands = sorted(candidates, key=lambda x: x.final_score, reverse=True)
        return sorted_cands
