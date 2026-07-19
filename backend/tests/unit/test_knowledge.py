from app.knowledge.service import KnowledgeService
from app.db.models.knowledge import Recipe, Ingredient, RecipeIngredient, Substitution

def test_get_recipe_ingredients(db_session):
    service = KnowledgeService(db_session)
    
    r = Recipe(name="Pasta")
    i1 = Ingredient(name="Tomato", normalized_name="tomato")
    i2 = Ingredient(name="Garlic", normalized_name="garlic")
    
    db_session.add(r)
    db_session.add(i1)
    db_session.add(i2)
    db_session.commit()
    
    ri1 = RecipeIngredient(recipe_id=r.id, ingredient_id=i1.id, quantity=2.0, unit="cups")
    ri2 = RecipeIngredient(recipe_id=r.id, ingredient_id=i2.id, quantity=1.0, unit="clove", is_optional=True)
    db_session.add(ri1)
    db_session.add(ri2)
    db_session.commit()
    
    ingredients = service.get_recipe_ingredients(r.id)
    assert len(ingredients) == 2

    assert ingredients[0]["name"] == "Tomato"
    assert ingredients[0]["quantity"] == 2.0
    
    assert ingredients[1]["name"] == "Garlic"
    assert ingredients[1]["is_optional"] is True

def test_find_substitutions(db_session):
    service = KnowledgeService(db_session)
    
    i1 = Ingredient(name="Sugar", normalized_name="sugar")
    i2 = Ingredient(name="Honey", normalized_name="honey")
    
    db_session.add_all([i1, i2])
    db_session.commit()
    
    sub = Substitution(ingredient_id=i1.id, substitute_ingredient_id=i2.id, confidence=0.8)
    db_session.add(sub)
    db_session.commit()
    
    subs = service.find_substitutions(i1.id, min_confidence=0.5)
    assert len(subs) == 1
    assert subs[0]["name"] == "Honey"
    assert subs[0]["confidence"] == 0.8

def test_expand_ingredients(db_session):
    service = KnowledgeService(db_session)
    
    i_butter = Ingredient(name="Butter", normalized_name="butter")
    i_margarine = Ingredient(name="Margarine", normalized_name="margarine")
    i_oil = Ingredient(name="Olive Oil", normalized_name="olive_oil")
    
    db_session.add_all([i_butter, i_margarine, i_oil])
    db_session.commit()
    
    # Butter can be substituted with margarine (high conf) or oil (low conf)
    sub1 = Substitution(ingredient_id=i_butter.id, substitute_ingredient_id=i_margarine.id, confidence=0.9)
    sub2 = Substitution(ingredient_id=i_butter.id, substitute_ingredient_id=i_oil.id, confidence=0.4)
    db_session.add_all([sub1, sub2])
    db_session.commit()
    
    # Expand ingredients should only include high confidence subs (>= 0.7 by default)
    expanded = service.expand_ingredients([i_butter.id])
    assert len(expanded) == 2
    assert i_butter.id in expanded
    assert i_margarine.id in expanded
