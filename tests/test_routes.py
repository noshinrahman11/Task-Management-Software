import pytest
from flask import url_for

def test_dashboard_access(test_client):
    """Ensure the dashboard page loads correctly"""
    response = test_client.get(url_for('dashboard'))
    assert response.status_code == 200  # Expecting success

def test_create_task(test_client):
    """Test if task creation works"""
    response = test_client.post(url_for('add_task'), data={
        "name": "Test Task",
        "description": "This is a test task",
        "status": "Not Started"
    })
    assert response.status_code == 302  # Redirect expected after submission




# def test_dashboard_access(test_client):
#     """Ensure the dashboard page loads correctly"""
#     response = test_client.get('/dashboard')
#     assert response.status_code == 200  # Expecting success

# def test_create_task(test_client):
#     """Test if task creation works"""
#     response = test_client.post('/add_task', data={
#         "name": "Test Task",
#         "description": "This is a test task",
#         "status": "Not Started"
#     })
#     assert response.status_code == 302  # Redirect expected after submission



