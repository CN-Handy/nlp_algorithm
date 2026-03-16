"""
Streamlit Demo Configuration
"""
import os

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_PREFIX = "/api/v1"

# Full API URL
BASE_URL = f"{API_BASE_URL}{API_PREFIX}"


def get_headers():
    """Get request headers"""
    return {
        "Content-Type": "application/json"
    }
