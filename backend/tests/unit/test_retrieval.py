import pytest
from app.engine.retrieval.hybrid import ResultMerger
from collections import namedtuple

# Create a mock product class for testing
MockProduct = namedtuple('MockProduct', ['id', 'name'])

def test_result_merger_overlapping_ids():
    prod1 = MockProduct(1, "Apple")
    prod2 = MockProduct(2, "Banana")
    prod3 = MockProduct(3, "Orange")

    semantic_res = [(prod1, 0.8), (prod2, 0.6)]
    fts_res = [(prod1, 0.9), (prod3, 0.5)]

    # Weights: semantic 0.7, fts 0.3
    merged = ResultMerger.merge(semantic_res, fts_res, 0.7, 0.3)
    
    # Check Prod 1 (overlapping)
    p1 = next(item for item in merged if item[0].id == 1)
    assert abs(p1[1] - (0.8 * 0.7 + 0.9 * 0.3)) < 0.001
    
    # Check Prod 2 (semantic only)
    p2 = next(item for item in merged if item[0].id == 2)
    assert abs(p2[1] - (0.6 * 0.7)) < 0.001
    
    # Check Prod 3 (fts only)
    p3 = next(item for item in merged if item[0].id == 3)
    assert abs(p3[1] - (0.5 * 0.3)) < 0.001

def test_result_merger_empty_fts():
    prod1 = MockProduct(1, "Apple")
    semantic_res = [(prod1, 0.8)]
    fts_res = []

    merged = ResultMerger.merge(semantic_res, fts_res, 0.7, 0.3)
    assert len(merged) == 1
    assert merged[0][1] == 0.8 * 0.7

def test_result_merger_empty_semantic():
    prod1 = MockProduct(1, "Apple")
    semantic_res = []
    fts_res = [(prod1, 0.5)]

    merged = ResultMerger.merge(semantic_res, fts_res, 0.7, 0.3)
    assert len(merged) == 1
    assert merged[0][1] == 0.5 * 0.3

def test_result_merger_both_empty():
    merged = ResultMerger.merge([], [], 0.7, 0.3)
    assert len(merged) == 0
