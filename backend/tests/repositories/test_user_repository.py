import pytest
from app.db.models.user import User
from app.db.repositories.user import UserRepository

def test_create_user(db_session):
    repo = UserRepository(db_session)
    user_in = {
        "email": "repo_test@cartpilot.ai",
        "hashed_password": "secure"
    }
    user = repo.create(user_in)
    
    assert user.id is not None
    assert user.email == "repo_test@cartpilot.ai"

def test_get_by_email(db_session):
    repo = UserRepository(db_session)
    user_in = {
        "email": "get@cartpilot.ai",
        "hashed_password": "secure"
    }
    repo.create(user_in)
    
    user = repo.get_by_email("get@cartpilot.ai")
    assert user is not None
    assert user.email == "get@cartpilot.ai"
