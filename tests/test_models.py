import pytest
from app import db
from models import User, Task  # Import necessary models

def test_create_user(test_client):
    user = User(username="testuser", email="test@example.com", Role="Staff")
    db.session.add(user)
    db.session.commit()
    
    retrieved_user = User.query.filter_by(username="testuser").first()
    assert retrieved_user is not None
    assert retrieved_user.email == "test@example.com"
