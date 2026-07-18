from typing import Dict, Any

class TemplateEngine:
    """
    Deterministic string interpolator. Prevents random LLM hallucinations 
    by restricting output to known, safe templates.
    """
    
    TEMPLATES = {
        "HEADER": "We selected {product_name} because:\n",
        "BRAND_AFFINITY": "• it matches your preferred brand ({brand})",
        "DIETARY_ALIGNMENT": "• it aligns with your {diet} diet",
        "CATEGORY_MATCH": "• it satisfies the {category_name} category",
        "IN_STOCK": "• it is currently in stock",
        "BUDGET_FIT": "• it fits perfectly within your allocated budget",
        "HIGH_RELEVANCE": "• it highly matches your specific goal requirements",
    }
    
    @classmethod
    def render(cls, template_key: str, context: Dict[str, Any] = None) -> str:
        if template_key not in cls.TEMPLATES:
            return ""
            
        template_str = cls.TEMPLATES[template_key]
        if context:
            try:
                return template_str.format(**context)
            except KeyError:
                return template_str # Fallback if context is missing
        return template_str
