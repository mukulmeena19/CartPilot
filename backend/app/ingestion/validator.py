from typing import List, Dict, Any

class Validator:
    def validate_openfoodfacts(self, parsed_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        valid = []
        for item in parsed_items:
            # Must have name, image, category, and some basic nutrition
            if not item.get("name"):
                continue
            if not item.get("image_url"):
                continue
            if not item.get("categories"):
                continue
            
            # Nutrition check
            nutriments = item.get("nutriments", {})
            if "energy-kcal_100g" not in nutriments and "proteins_100g" not in nutriments:
                continue
                
            valid.append(item)
        return valid
