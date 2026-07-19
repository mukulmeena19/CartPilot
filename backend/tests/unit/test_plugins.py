import pytest
from app.engine.ranking.plugins import PluginRanker, RankingPlugin

class MockPluginA(RankingPlugin):
    def score(self, item, context):
        return getattr(item, "score_a", 0.0)

class MockPluginB(RankingPlugin):
    def score(self, item, context):
        if getattr(item, "fail", False):
            raise ValueError("Simulated failure")
        return getattr(item, "score_b", 0.0)

class DummyItem:
    def __init__(self, name, score_a, score_b, fail=False):
        self.name = name
        self.score_a = score_a
        self.score_b = score_b
        self.fail = fail

def test_plugin_ranker_weights():
    plugins = {
        "A": MockPluginA(),
        "B": MockPluginB()
    }
    weights = {"A": 0.8, "B": 0.2}
    ranker = PluginRanker(plugins, weights)
    
    items = [
        DummyItem("Item 1", score_a=1.0, score_b=0.0), # A wins
        DummyItem("Item 2", score_a=0.5, score_b=0.5), # Mixed
        DummyItem("Item 3", score_a=0.0, score_b=1.0)  # B wins
    ]
    
    ranked = ranker.rank(items, {})
    
    assert ranked[0].name == "Item 1"
    assert ranked[0].final_rank_score == (1.0 * 0.8 + 0.0 * 0.2) / 1.0
    
    assert ranked[1].name == "Item 2"
    assert ranked[1].final_rank_score == (0.5 * 0.8 + 0.5 * 0.2) / 1.0

def test_plugin_ranker_graceful_failure():
    plugins = {
        "A": MockPluginA(),
        "B": MockPluginB()
    }
    weights = {"A": 0.5, "B": 0.5}
    ranker = PluginRanker(plugins, weights)
    
    items = [
        DummyItem("Item 1", score_a=1.0, score_b=1.0, fail=True), 
        DummyItem("Item 2", score_a=0.5, score_b=0.5, fail=False) 
    ]
    
    ranked = ranker.rank(items, {})
    
    # Item 1 failed on B, so B returns 0.0. Total = 1.0 * 0.5 + 0.0 * 0.5 = 0.5
    # Item 2 didn't fail. Total = 0.5 * 0.5 + 0.5 * 0.5 = 0.5
    assert ranked[0].final_rank_score == 0.5
    assert ranked[1].final_rank_score == 0.5
