from app.intelligence.personalization.engine import PersonalizationEngine
from app.ai.retrieval.models import ProductCandidate

def test_cold_start_profile(db_session):
    engine = PersonalizationEngine(db_session)
    
    # Needs a User first
    from app.db.models.user import User
    user = User(email="test@cartpilot.ai", hashed_password="pw")
    db_session.add(user)
    db_session.commit()
    
    profile = engine.cold_start_profile(user.id, {"cuisines": {"Italian": 0.8}, "brands": {"Amul": 0.9}})
    assert profile.user_id == user.id

def test_calculate_affinity(db_session):
    engine = PersonalizationEngine(db_session)
    
    # Needs a User first
    from app.db.models.user import User
    user = User(email="test@cartpilot.ai", hashed_password="pw")
    db_session.add(user)
    db_session.commit()
    
    # Cold start
    profile = engine.cold_start_profile(user.id, {"cuisines": {"Italian": 0.8}, "brands": {"Amul": 0.9}})
    assert profile.user_id == user.id
    
    candidates = [
        ProductCandidate(product_id=1, product_name="Amul Cheese", category_name="Cheese", price=5.0, similarity_score=0.8, embedding_model="test", brand="Amul"),
        ProductCandidate(product_id=2, product_name="Other Cheese", category_name="Cheese", price=4.0, similarity_score=0.8, embedding_model="test", brand="Other")
    ]
    
    # Calculate affinity
    aff_candidates = engine.calculate_affinity(user.id, candidates)
    
    # Amul should be bumped higher
    assert aff_candidates[0].brand == "Amul"
    assert aff_candidates[0].similarity_score > 0.8

def test_update_preferences(db_session):
    engine = PersonalizationEngine(db_session)
    
    from app.db.models.user import User
    user = User(email="test1@cartpilot.ai", hashed_password="pw")
    db_session.add(user)
    db_session.commit()
    
    engine.update_preferences(user.id, "cuisine", "Mexican", 0.5, source="implicit")
    
    # Let's see if we can generate filters, Mexican shouldn't exclude anything
    filters = engine.generate_filters(user.id)
    assert "exclude_ingredients" not in filters

def test_generate_filters(db_session):
    engine = PersonalizationEngine(db_session)
    
    from app.db.models.user import User
    user = User(email="test2@cartpilot.ai", hashed_password="pw")
    db_session.add(user)
    db_session.commit()
    
    # -1.0 affinity means allergy/hate
    engine.update_preferences(user.id, "allergy", "Peanut", -1.0, source="explicit")
    engine.update_preferences(user.id, "dietary", "Vegan", 1.0, source="explicit")
    
    filters = engine.generate_filters(user.id)
    assert "Peanut" in filters["exclude_ingredients"]
