# Predefined macro splits for specific dietary profiles.
# These represent minimum budget percentages that MUST go to these categories if the profile is detected.
DIETARY_CONSTRAINTS = {
    "high_protein": {
        "Protein": 0.45,       # Minimum 45% of budget
        "Vegetables": 0.20,
    },
    "vegan": {
        "Vegetables": 0.35,
        "Protein": 0.25,       # Plant-based protein
        "Carbohydrates": 0.25,
    },
    "vegetarian": {
        "Vegetables": 0.30,
        "Protein": 0.20,
        "Dairy": 0.15,
        "Carbohydrates": 0.25,
    },
    "keto": {
        "Protein": 0.40,
        "Dairy": 0.20,
        "Vegetables": 0.20,
        "Fats": 0.15,
    }
}

DEFAULT_CATEGORIES = [
    "Protein",
    "Vegetables",
    "Carbohydrates",
    "Dairy",
    "Fruits",
    "Pantry",
    "Snacks"
]
