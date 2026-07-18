from datetime import datetime, timezone
from app.ai.memory.models import PreferenceSignal, UserPreferenceContext

class PreferenceExtractor:
    @staticmethod
    def apply_signal(
        context: UserPreferenceContext,
        preference_type: str, # 'brands', 'dietary', 'allergies'
        value: str,
        action: str, # 'positive' or 'negative'
        source: str = "inferred"
    ) -> UserPreferenceContext:
        """
        Applies mathematical growth or decay to a preference confidence.
        """
        # Ensure the attribute exists
        if not hasattr(context, preference_type):
            return context
            
        target_dict = getattr(context, preference_type)
        
        # Growth and decay constants
        GROWTH_STEP = 0.1
        DECAY_STEP = 0.2
        
        # If explicit, start at 1.0. If inferred, start lower.
        base_confidence = 1.0 if source == "explicit" else 0.5
        
        if value not in target_dict:
            # First time seeing this signal
            if action == "positive":
                target_dict[value] = PreferenceSignal(
                    value=value,
                    confidence=base_confidence,
                    source=source,
                    last_updated=datetime.now(timezone.utc)
                )
            else:
                # If the very first action is negative, we store it with high confidence 
                # to ensure we remember they disliked it. But we prefix it or handle it.
                # Since our schema just tracks "how strongly they prefer", a negative action 
                # on a brand they don't even have a preference for means we want to explicitly dislike it.
                # To keep it simple, we could use a separate "disliked_brands" or we map negative 
                # to a different structure. 
                # For this design, let's treat "action=negative" as reducing confidence of preference.
                # If it's a new item, they don't prefer it, so we don't add it to "preferred" list.
                pass 
        else:
            # Modifying existing signal
            existing = target_dict[value]
            
            # Explicit rules override inferred decay
            if existing.source == "explicit" and source == "inferred":
                # Do not let inferred actions decay explicit settings easily
                DECAY_STEP = 0.05
                GROWTH_STEP = 0.05
                
            if action == "positive":
                existing.confidence = min(1.0, existing.confidence + GROWTH_STEP)
            else:
                existing.confidence = max(0.0, existing.confidence - DECAY_STEP)
                
            existing.last_updated = datetime.now(timezone.utc)
            
            # If confidence hits 0, remove the preference
            if existing.confidence <= 0:
                del target_dict[value]
                
        return context
