from typing import List
from app.ai.optimization.models import OptimizedCandidate
from app.ai.explainability.models import ProductExplanation
from app.ai.explainability.reasoning_formatter import ReasoningFormatter
from app.ai.explainability.template_engine import TemplateEngine

class ExplanationBuilder:
    @staticmethod
    def build_explanation(candidate: OptimizedCandidate) -> ProductExplanation:
        
        # 1. Parse raw trace into rule codes
        extracted_rules = ReasoningFormatter.extract_rules(candidate)
        
        # 2. Render Header
        explanation_lines = [
            TemplateEngine.render("HEADER", {"product_name": candidate.candidate.candidate.product_name})
        ]
        
        supporting_rules = []
        preference_applied = False
        
        # 3. Render Bullets
        for rule_key, context in extracted_rules:
            rendered = TemplateEngine.render(rule_key, context)
            if rendered:
                explanation_lines.append(rendered)
                supporting_rules.append(rule_key)
                
                if rule_key in ["BRAND_AFFINITY", "DIETARY_ALIGNMENT"]:
                    preference_applied = True
                    
        # 4. Assemble String
        final_text = "\n".join(explanation_lines)
        
        # 5. Wrap in Schema
        return ProductExplanation(
            product_id=candidate.candidate.candidate.product_id,
            product_name=candidate.candidate.candidate.product_name,
            explanation_text=final_text,
            supporting_rules=supporting_rules,
            optimization_score=candidate.final_score,
            verification_status=candidate.candidate.verification_status,
            budget_fit=True, # Assumed True if it made it to the final cart
            preference_applied=preference_applied
        )
