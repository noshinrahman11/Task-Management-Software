import pytest
from flask import url_for

def test_register_user(client):
    """Test user registration"""
    with client.application.app_context():
        response = client.post(url_for('register'), data={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password-123",
            "confirm_password": "password-123",
            "FirstName": "Name",
            "LastName": "Name",
            "BirthDate": "2025-03-22 00:00:00.000000",
            "Role": "Staff"
        })
        assert response.status_code == 302  # Expecting redirect to login

def test_login_user(client):
    """Test user login"""
    with client.application.app_context():
        response = client.post(url_for('login'), data={
            "email": "newuser@example.com",
            "password": "password-123"
        })
        assert response.status_code == 302  # Expecting redirect after login