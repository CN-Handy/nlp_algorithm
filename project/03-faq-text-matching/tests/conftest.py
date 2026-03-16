"""
Pytest configuration and fixtures for FAQ API tests
"""
import pytest
import requests

# Base URL for API
BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="session")
def base_url():
    """Base URL fixture"""
    return BASE_URL


@pytest.fixture(scope="session")
def auth_token():
    """Authentication token fixture - replace with actual token"""
    return "test_token_12345"


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    """Authorization headers fixture"""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    }


@pytest.fixture
def base_headers():
    """Base headers without auth"""
    return {
        "Content-Type": "application/json"
    }


# Store created IDs for cleanup
@pytest.fixture
def created_category_ids():
    """Track created category IDs for cleanup"""
    return []


@pytest.fixture
def created_faq_ids():
    """Track created FAQ IDs for cleanup"""
    return []
