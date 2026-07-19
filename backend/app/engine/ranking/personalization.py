from typing import Dict, Any
from app.engine.models import CandidateScore, PluginResult
from app.engine.ranking.plugins import RankingPlugin

class PersonalizationPlugin(RankingPlugin):
    def score(self, candidate: CandidateScore, context: Dict[str, Any]) -> PluginResult:
        # Context should contain 'user_intelligence' dict
        user_intel = context.get("user_intelligence", {})
        if not user_intel:
            return PluginResult(score=0.0, weight=1.0)
            
        item = candidate.item
        brand = getattr(item, "brand", None)
        category = getattr(item, "category_name", None)
        
        score = 0.0
        reasons = []
        
        # 1. Brand affinity
        brand_affinities = user_intel.get("brand_affinities", {})
        if brand and brand in brand_affinities:
            b_score = brand_affinities[brand]
            score += b_score
            if b_score > 0.6:
                reasons.append(f"From your preferred brand {brand}")
                
        # 2. Frequent purchases (category/items)
        freq_cats = user_intel.get("frequent_categories", [])
        if category and category in freq_cats:
            score += 0.5
            reasons.append(f"You frequently buy {category}")
            
        # Normalize score
        final_score = min(1.0, score)
        reason_str = " and ".join(reasons) if reasons else None
        
        return PluginResult(score=final_score, reason=reason_str, weight=1.2)
