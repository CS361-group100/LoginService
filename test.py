import os
import pytest
from flask import json
from login_service import app

# Set the REDIS_URL for testing, if necessary
os.environ['REDIS_URL'] = 'memory://'

@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_register_success(client):
    """Test user registration successful case."""
    response = client.post('/auth/register', json={
        'username': 'testuser',
        'password': 'StrongPassword123'
    })
    assert response.status_code == 201
    assert response.get_json() == {"message": "User created. Please sign in."}

def test_register_conflict(client):
    """Test user registration conflict case (username already taken)."""
    client.post('/auth/register', json={
        'username': 'testuser',
        'password': 'StrongPassword123'
    })  # Register first user

    response = client.post('/auth/register', json={
        'username': 'testuser',
        'password': 'AnotherPassword456'
    })
    assert response.status_code == 409
    assert response.get_json() == {
        "error": "conflict",
        "message": "Username already in use"
    }

def test_login_success(client):
    """Test successful user login."""
    client.post('/auth/register', json={
        'username': 'testuser',
        'password': 'StrongPassword123'
    })  # Register the user first

    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'StrongPassword123'
    })
    assert response.status_code == 200
    assert 'accessToken' in response.get_json()

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    client.post('/auth/register', json={
        'username': 'testuser',
        'password': 'StrongPassword123'
    })  # Register the user first

    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'WrongPassword'
    })
    assert response.status_code == 401
    assert response.get_json() == {
        "error": "INVALID_CREDENTIALS",
        "message": "Email or password is incorrect."
    }

def test_login_block_after_failed_attempts(client):
    """Test login block after exceeding failed attempts."""
    client.post('/auth/register', json={
        'username': 'testuser',
        'password': 'StrongPassword123'
    })  # Register the user first

    for _ in range(5):  # Exceed the limit
        client.post('/auth/login', json={
            'username': 'testuser',
            'password': 'WrongPassword'
        })

    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'StrongPassword123'
    })
    assert response.status_code == 403
    assert response.get_json() == {
        "error": "You are blocked from logging in for 20 minutes."
    }