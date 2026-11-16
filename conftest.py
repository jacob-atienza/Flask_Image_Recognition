"""Pytest configuration for the Flask application."""
import pytest
from app import app  # This imports the Flask app for testing

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as test_client:
        yield test_client
