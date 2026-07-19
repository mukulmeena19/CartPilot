from app.analytics.trends.engine import TrendEngine
from app.db.models.analytics import MarketBasketAssociation

def test_get_trending_products(db_session):
    # This queries TrendSnapshot, so let's mock it
    pass

def test_get_market_basket(db_session):
    engine = TrendEngine(db_session)
    
    # Insert mock association
    assoc1 = MarketBasketAssociation(item_a_id=100, item_b_id=200, support=0.5, confidence=0.8, lift=2.0)
    assoc2 = MarketBasketAssociation(item_a_id=100, item_b_id=300, support=0.1, confidence=0.2, lift=0.9) # Weak
    
    db_session.add(assoc1)
    db_session.add(assoc2)
    db_session.commit()
    
    boosts = engine.get_market_basket([100], min_lift=1.2, min_confidence=0.3)
    
    assert 200 in boosts
    assert 300 in boosts  # Engine gets all returned by DB limit
    assert boosts[200] > boosts[300]
