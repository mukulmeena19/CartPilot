from app.ai.retrieval.models import ProductCandidate

class PricingChecker:
    @staticmethod
    def is_price_valid(candidate: ProductCandidate) -> bool:
        """
        Validates that the price is greater than 0 and mathematically sane.
        (Future-proofing: Could inject promotional checks here).
        """
        if candidate.price <= 0:
            return False
            
        # Example extreme upper bound sanity check for groceries
        if candidate.price > 5000:
            return False
            
        return True
