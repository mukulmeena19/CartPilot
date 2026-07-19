import pytest
from app.engine.models import CandidateScore
from app.engine.constraints import ConstraintFilter
from app.engine.ranking.plugins import ExplainablePluginRanker, BudgetOptimizerPlugin, NutritionScorePlugin
from app.engine.ranking.personalization import PersonalizationPlugin

class MockProduct:
    def __init__(self, id, name, price, dietary_tags=None, nutrition=None):
        self.id = id
        self.name = name
        self.price = price
        self.dietary_tags = dietary_tags or []
        self.nutrition = nutrition or {}

@pytest.fixture
def mock_candidates():
    return [
        CandidateScore(
            candidate_id="1", 
            item=MockProduct(1, "Premium Protein Bar", 150.0, ["High Protein"], {"protein": 20.0}),
            semantic_score=0.9, fts_score=0.8, final_score=0.85
        ),
        CandidateScore(
            candidate_id="2", 
            item=MockProduct(2, "Cheap Yogurt", 40.0, ["Vegetarian"], {"protein": 5.0}),
            semantic_score=0.7, fts_score=0.5, final_score=0.6
        ),
        CandidateScore(
            candidate_id="3", 
            item=MockProduct(3, "Expensive Tofu", 200.0, ["Vegan", "Vegetarian"], {"protein": 15.0}),
            semantic_score=0.6, fts_score=0.6, final_score=0.6
        )
    ]

def test_budget_constraint(mock_candidates):
    # Filter items over 100
    context = {"max_budget": 100.0}
    filtered = ConstraintFilter.apply(mock_candidates, context)
    assert len(filtered) == 1
    assert filtered[0].item.name == "Cheap Yogurt"

def test_dietary_constraint(mock_candidates):
    # Filter only Vegan
    context = {"dietary_requirement": "Vegan"}
    filtered = ConstraintFilter.apply(mock_candidates, context)
    assert len(filtered) == 1
    assert filtered[0].item.name == "Expensive Tofu"

def test_empty_budget_constraint(mock_candidates):
    # Zero budget should filter out everything
    context = {"max_budget": 0.0}
    filtered = ConstraintFilter.apply(mock_candidates, context)
    assert len(filtered) == 0

def test_extreme_budget_constraint(mock_candidates):
    # Extremely large budget should allow everything
    context = {"max_budget": 99999.0}
    filtered = ConstraintFilter.apply(mock_candidates, context)
    assert len(filtered) == 3

def test_budget_optimizer_plugin(mock_candidates):
    ranker = ExplainablePluginRanker(plugins={"budget": BudgetOptimizerPlugin()})
    context = {"target_budget": 100.0}
    # Candidates 1, 2, 3 have prices 150, 40, 200
    # 40 is <= 50% of 100 (Score 1.0)
    # 150 > 100 (Score 0.0)
    ranked = ranker.rank(mock_candidates, context)
    
    c2 = next(c for c in ranked if c.candidate_id == "2")
    assert c2.plugin_results["budget"].score == 1.0
    
    c1 = next(c for c in ranked if c.candidate_id == "1")
    assert c1.plugin_results["budget"].score == 0.0

def test_nutrition_score_plugin(mock_candidates):
    ranker = ExplainablePluginRanker(plugins={"nutrition": NutritionScorePlugin()})
    context = {"protein_target": 20.0}
    ranked = ranker.rank(mock_candidates, context)
    
    c1 = next(c for c in ranked if c.candidate_id == "1")
    assert c1.plugin_results["nutrition"].score == 1.0
    
    c3 = next(c for c in ranked if c.candidate_id == "3")
    assert c3.plugin_results["nutrition"].score == 0.5  # 15 >= 10
    
    c2 = next(c for c in ranked if c.candidate_id == "2")
    assert c2.plugin_results["nutrition"].score == 0.0  # 5 < 10

def test_empty_candidates_handling():
    ranker = ExplainablePluginRanker(plugins={"budget": BudgetOptimizerPlugin()})
    ranked = ranker.rank([], {"target_budget": 100.0})
    assert ranked == []
