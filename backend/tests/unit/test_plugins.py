import pytest
from app.engine.ranking.plugins import ExplainablePluginRanker, RankingPlugin
from app.engine.models import CandidateScore, PluginResult


class MockPluginA(RankingPlugin):
    def score(self, candidate, context):
        val = getattr(candidate.item, "score_a", 0.0)
        return PluginResult(score=val, weight=1.0, reason="Plugin A" if val > 0 else "")


class MockPluginB(RankingPlugin):
    def score(self, candidate, context):
        if getattr(candidate.item, "fail", False):
            raise ValueError("Simulated failure")
        val = getattr(candidate.item, "score_b", 0.0)
        return PluginResult(score=val, weight=1.0, reason="Plugin B" if val > 0 else "")


class DummyItem:
    def __init__(self, name, score_a, score_b, fail=False):
        self.name = name
        self.score_a = score_a
        self.score_b = score_b
        self.fail = fail


def _make_candidate(item, cid):
    return CandidateScore(candidate_id=cid, item=item, final_score=0.0)


def test_plugin_ranker_weights():
    plugins = {
        "A": MockPluginA(),
        "B": MockPluginB()
    }
    weights = {"A": 0.8, "B": 0.2}
    ranker = ExplainablePluginRanker(plugins, weights)

    items = [
        _make_candidate(DummyItem("Item 1", score_a=1.0, score_b=0.0), "1"),
        _make_candidate(DummyItem("Item 2", score_a=0.5, score_b=0.5), "2"),
        _make_candidate(DummyItem("Item 3", score_a=0.0, score_b=1.0), "3"),
    ]

    ranked = ranker.rank(items, {})

    # Item 1: plugin_score = (1.0*0.8 + 0.0*0.2) / 1.0 = 0.8, final = 0.0*0.5 + 0.8*0.5 = 0.4
    # Item 2: plugin_score = (0.5*0.8 + 0.5*0.2) / 1.0 = 0.5, final = 0.0*0.5 + 0.5*0.5 = 0.25
    # Item 3: plugin_score = (0.0*0.8 + 1.0*0.2) / 1.0 = 0.2, final = 0.0*0.5 + 0.2*0.5 = 0.1
    assert ranked[0].item.name == "Item 1"
    assert ranked[1].item.name == "Item 2"
    assert ranked[2].item.name == "Item 3"


def test_plugin_ranker_graceful_failure():
    plugins = {
        "A": MockPluginA(),
        "B": MockPluginB()
    }
    weights = {"A": 0.5, "B": 0.5}
    ranker = ExplainablePluginRanker(plugins, weights)

    items = [
        _make_candidate(DummyItem("Item 1", score_a=1.0, score_b=1.0, fail=True), "1"),
        _make_candidate(DummyItem("Item 2", score_a=0.5, score_b=0.5, fail=False), "2"),
    ]

    # Should not crash even though Plugin B throws for Item 1
    ranked = ranker.rank(items, {})
    assert len(ranked) == 2
