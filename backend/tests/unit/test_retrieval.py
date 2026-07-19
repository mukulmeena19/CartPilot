"""
Tests for the hybrid retrieval merge logic.
Since the merging is done inside HybridRetriever.retrieve_candidates (which requires a DB session),
we test the merge math in isolation here using a lightweight helper.
"""
import pytest
import math
from collections import namedtuple

MockProduct = namedtuple('MockProduct', ['id', 'name'])


def merge_scores(semantic_res, fts_res, semantic_w=0.7, fts_w=0.3):
    """
    Pure-function reimplementation of the merge logic inside HybridRetriever,
    so we can test the math without needing a database.
    """
    candidates = {}

    for item, score in semantic_res:
        c_id = str(item.id)
        if c_id not in candidates:
            candidates[c_id] = {"item": item, "semantic": 0.0, "fts": 0.0}
        candidates[c_id]["semantic"] = score

    for item, score in fts_res:
        c_id = str(item.id)
        if c_id not in candidates:
            candidates[c_id] = {"item": item, "semantic": 0.0, "fts": 0.0}
        candidates[c_id]["fts"] = score

    results = []
    for c_id, data in candidates.items():
        final = data["semantic"] * semantic_w + data["fts"] * fts_w
        results.append((data["item"], final))

    return sorted(results, key=lambda x: x[1], reverse=True)


def test_merge_overlapping_ids():
    prod1 = MockProduct(1, "Apple")
    prod2 = MockProduct(2, "Banana")
    prod3 = MockProduct(3, "Orange")

    semantic_res = [(prod1, 0.8), (prod2, 0.6)]
    fts_res = [(prod1, 0.9), (prod3, 0.5)]

    merged = merge_scores(semantic_res, fts_res, 0.7, 0.3)

    p1 = next(item for item in merged if item[0].id == 1)
    assert abs(p1[1] - (0.8 * 0.7 + 0.9 * 0.3)) < 0.001

    p2 = next(item for item in merged if item[0].id == 2)
    assert abs(p2[1] - (0.6 * 0.7)) < 0.001

    p3 = next(item for item in merged if item[0].id == 3)
    assert abs(p3[1] - (0.5 * 0.3)) < 0.001


def test_merge_empty_fts():
    prod1 = MockProduct(1, "Apple")
    semantic_res = [(prod1, 0.8)]
    fts_res = []

    merged = merge_scores(semantic_res, fts_res, 0.7, 0.3)
    assert len(merged) == 1
    assert abs(merged[0][1] - 0.8 * 0.7) < 0.001


def test_merge_empty_semantic():
    prod1 = MockProduct(1, "Apple")
    semantic_res = []
    fts_res = [(prod1, 0.5)]

    merged = merge_scores(semantic_res, fts_res, 0.7, 0.3)
    assert len(merged) == 1
    assert abs(merged[0][1] - 0.5 * 0.3) < 0.001


def test_merge_both_empty():
    merged = merge_scores([], [], 0.7, 0.3)
    assert len(merged) == 0


def test_fts_normalization():
    """Test that our FTS score normalization formula maps correctly."""
    # 1 - e^(-rank) should map rank=0 → 0, rank→∞ → 1
    assert abs((1.0 - math.exp(0.0)) - 0.0) < 0.001
    assert (1.0 - math.exp(-5.0)) > 0.99
    # rank=1 should give ~0.632
    assert abs((1.0 - math.exp(-1.0)) - 0.6321) < 0.001
