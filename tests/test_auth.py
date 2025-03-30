import pytest
from flask import url_for

def test_register_user(test_client):
    """Test user registration"""
    response = test_client.post(url_for('register'), data={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })
    assert response.status_code == 302  # Expecting redirect to login

def test_login_user(test_client):
    """Test user login"""
    response = test_client.post(url_for('login'), data={
        "email": "newuser@example.com",
        "password": "password123"
    })
    assert response.status_code == 302  # Expecting redirect after login





# def test_register_user(test_client):
#     """Test user registration"""
#     response = test_client.post('/register', data={
#         "username": "newuser",
#         "email": "newuser@example.com",
#         "password": "password123",
#         "confirm_password": "password123"
#     })
#     assert response.status_code == 302  # Expecting redirect to login

# def test_login_user(test_client):
#     """Test user login"""
#     response = test_client.post('/login', data={
#         "email": "newuser@example.com",
#         "password": "password123"
#     })
#     assert response.status_code == 302  # Expecting redirect after login