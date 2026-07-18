# Base weights for the scoring equation
# Final Score = (Sim * W_SIM) + (Verif * W_VERIF) + (PrefBonus * W_PREF)
WEIGHT_SEMANTIC_SIMILARITY = 0.4
WEIGHT_VERIFICATION_SCORE = 0.3
WEIGHT_PREFERENCE_BONUS = 0.3

# Constraint Settings
# How far above the estimated category budget are we willing to go if it's the absolute best item?
MAX_BUDGET_OVERRIDE_RATIO = 1.2 

# Diversity Settings
# Penalty applied if the same brand is selected multiple times in a diverse basket
BRAND_DUPLICATION_PENALTY = 0.15
