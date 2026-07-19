import logging
from typing import List, Dict, Any
from app.engine.models import CandidateScore

logger = logging.getLogger(__name__)

class ConstraintFilter:
    @staticmethod
    def apply(candidates: List[CandidateScore], constraints: Dict[str, Any]) -> List[CandidateScore]:
        """
        Applies hard business constraints, completely removing invalid candidates.
        """
        filtered = []
        for c in candidates:
            item = c.item
            keep = True
            
            # 1. Budget ceiling
            max_budget = constraints.get("max_budget")
            if max_budget is not None and hasattr(item, "price"):
                if item.price > max_budget:
                    keep = False
            
            # 2. Vegan/Vegetarian (Dietary)
            dietary_req = constraints.get("dietary_requirement")
            if keep and dietary_req and hasattr(item, "dietary_tags"):
                # If item lacks the required tag, filter out
                tags = getattr(item, "dietary_tags", [])
                if not tags or dietary_req not in tags:
                    keep = False
                    
            # 3. Allergies
            allergies = constraints.get("allergies", [])
            if keep and allergies and hasattr(item, "ingredients"):
                # A simplistic check: if any allergy string is in the item's ingredients text
                # We would want a more robust structured check in a real scenario
                ingredients_text = str(getattr(item, "ingredients", "")).lower()
                for allergy in allergies:
                    if allergy.lower() in ingredients_text:
                        keep = False
                        break
                        
            # 4. Out of stock
            # We assume item has an 'inventory' relationship or 'is_active' flag.
            if keep and hasattr(item, "inventory"):
                inv = getattr(item, "inventory")
                if inv and inv.quantity_available <= 0:
                    keep = False
            
            if keep:
                filtered.append(c)
                
        logger.info(f"Constraints removed {len(candidates) - len(filtered)} candidates.")
        return filtered
