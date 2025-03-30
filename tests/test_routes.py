import pytest
from flask import url_for
from __init__ import create_app  # Import your create_app function


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app("testing")  # Pass a test config if needed
    with app.app_context():  # Ensures Flask has an active app context
        yield app  # Provide the app to the test

@pytest.fixture
def client(app):
    """Create a test client for making requests."""
    return app.test_client()

def test_homepage(client):
    """Test if homepage loads correctly"""
    with client.application.app_context():
        response = client.get(url_for('dashboard'))
        assert response.status_code == 200
        assert b"Welcome" in response.data  # Check if "Welcome" text appears


def test_create_task(client):
    response = client.post('/dashboard', data={ 
        'taskName': 'New Task',
        'description': 'Test Task Description',
        'startDate': '2025-03-01T10:00',
        'dueDate': '2025-03-01T12:00',
        'category': 'General',
        'status': 'Pending',
        'priority': 'High',
        'assignedTo': 'user_id'
     })
    assert response.status_code == 200  # Expecting a redirect
