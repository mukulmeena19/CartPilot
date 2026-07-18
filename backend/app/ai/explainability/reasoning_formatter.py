from typing import List, Dict, Any, Tuple
from app.ai.optimization.models import OptimizedCandidate

class ReasoningFormatter:
    """
    Parses the internal OptimizationTrace and translates raw mathematical 
    bonuses into structured Rule Codes and Context dictionaries for the Template Engine.
    """
    
    @staticmethod
    def extract_rules(candidate: OptimizedCandidate) -> List[Tuple[str, Dict[str, Any]]]:
        rules = []
        trace = candidate.optimization_trace
        
        # 1. Category Mapping
        rules.append(("CATEGORY_MATCH", {"category_name": candidate.candidate.candidate.category_name}))
        
        # 2. Inventory Mapping (we know it's in stock if it survived verification)
        if candidate.candidate.stock_available:
            rules.append(("IN_STOCK", {}))
            
        # 3. Relevance / Similarity
        # If the base similarity was very high (> 0.8), highlight it
        if candidate.candidate.candidate.similarity_score > 0.8:
            rules.append(("HIGH_RELEVANCE", {}))
            
        # 4. Budget Mapping (we know it fits because constraint engine passed it, but we can just append it safely)
        rules.append(("BUDGET_FIT", {}))
        
        # 5. Preference Parsing
        # The scoring engine outputs strings like "Brand Affinity (Amul: +0.30)"
        for bonus in trace.bonuses_applied:
            if "Brand Affinity" in bonus:
                # Extract brand name safely
                try:
                    brand_name = bonus.split("(")[1].split(":")[0].strip()
                    rules.append(("BRAND_AFFINITY", {"brand": brand_name}))
                except Exception:
                    pass
            elif "Dietary Alignment" in bonus:
                try:
                    diet_name = bonus.split("(")[1].split(":")[0].strip()
                    rules.append(("DIETARY_ALIGNMENT", {"diet": diet_name}))
                except Exception:
                    pass
                    
        return rules
