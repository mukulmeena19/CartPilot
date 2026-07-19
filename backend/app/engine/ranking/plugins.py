"""
Plugin-based Ranking Engine.
Computes the final score for retrieved items using multiple signals.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class RankingPlugin(ABC):
    """Abstract base class for all ranking plugins."""
    
    @abstractmethod
    def score(self, item: Any, context: Dict[str, Any]) -> float:
        """Return a score between 0.0 and 1.0"""
        pass


class SemanticSimilarityPlugin(RankingPlugin):
    def score(self, item: Any, context: Dict[str, Any]) -> float:
        # Expected to be populated by the Retriever (e.g. via pgvector distance)
        return getattr(item, "similarity_score", 0.5)


class BrandAffinityPlugin(RankingPlugin):
    def score(self, item: Any, context: Dict[str, Any]) -> float:
        brand_affinities = context.get("brand_affinities", {})
        return brand_affinities.get(getattr(item, "brand", ""), 0.0)


class PluginRanker:
    def __init__(self, plugins: Dict[str, RankingPlugin], weights: Dict[str, float]):
        self.plugins = plugins
        self.weights = weights

    def rank(self, items: List[Any], context: Dict[str, Any]) -> List[Any]:
        """
        Ranks items by applying all plugins and their respective weights.
        """
        for item in items:
            total_score = 0.0
            for name, plugin in self.plugins.items():
                weight = self.weights.get(name, 1.0)
                total_score += plugin.score(item, context) * weight
            setattr(item, "final_rank_score", total_score)
            
        return sorted(items, key=lambda x: getattr(x, "final_rank_score", 0.0), reverse=True)
