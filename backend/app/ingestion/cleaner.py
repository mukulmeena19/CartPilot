from typing import List, Dict, Any

class Cleaner:
    def clean_openfoodfacts(self, valid_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned = []
        for item in valid_items:
            # Clean categories (take first main category)
            raw_categories = item.get("categories", "")
            cat_list = [c.strip() for c in raw_categories.split(",") if c.strip()]
            primary_category = cat_list[0] if cat_list else "Groceries"
            
            # Clean brand
            brand = item.get("brand")
            if brand:
                brand = brand.split(",")[0].strip()
                
            # Clean nutrition
            nutriments = item.get("nutriments", {})
            nutrition = {
                "protein": nutriments.get("proteins_100g", 0.0),
                "calories": nutriments.get("energy-kcal_100g", 0.0),
                "carbs": nutriments.get("carbohydrates_100g", 0.0),
                "fat": nutriments.get("fat_100g", 0.0),
            }
            
            # Mock price and unit for now, as OFF doesn't provide price
            # We can use a hash of the id to generate a consistent fake price
            fake_price = float((hash(item["id"]) % 400) + 50) 
            
            cleaned.append({
                "id": item["id"],
                "name": item["name"].strip(),
                "brand": brand,
                "category_name": primary_category,
                "price": fake_price,
                "unit": item.get("quantity") or "piece",
                "nutrition": nutrition,
                "image_url": item["image_url"],
                "description": f"Product from Open Food Facts. {primary_category}.",
            })
        return cleaned
