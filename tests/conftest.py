import pytest
import os
from database import db_sessions, init_db, drop_db
from __init__ import create_app, Config, TestingConfig

@pytest.fixture(scope="session")
def test_app():
    """Set up a test instance of Flask app"""
    os.environ["TESTING"] = "True"  # Set testing mode
    app = create_app("testing")  # Use 'testing' to trigger TestingConfig
    with app.app_context():
        init_db()  # Create tables for testing
    yield app
    with app.app_context():
        drop_db()  # Cleanup after all tests

@pytest.fixture(scope="function")
def client(test_app):
    """Creates a test client for making requests"""
    return test_app.test_client()

@pytest.fixture(scope="function")
def db_session(test_app):
    """Provides a clean database session for each test"""
    with test_app.app_context():
        db_sessions.begin_nested()  # Start a new transaction
        yield db_sessions
        db_sessions.rollback()  # Rollback changes after each test