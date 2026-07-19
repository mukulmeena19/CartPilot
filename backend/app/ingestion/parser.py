from typing import List, Dict, Any

class BaseParser:
    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        raise NotImplementedError

class OpenFoodFactsParser(BaseParser):
    def parse(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parses raw Open Food Facts JSON response.
        Expected format: {"products": [{...}, {...}]}
        """
        products = raw_data.get("products", [])
        parsed = []
        for p in products:
            parsed.append({
                "id": p.get("_id"),
                "name": p.get("product_name"),
                "brand": p.get("brands"),
                "categories": p.get("categories"),
                "image_url": p.get("image_url"),
                "nutriments": p.get("nutriments", {}),
                "quantity": p.get("quantity")
            })
        return parsed
