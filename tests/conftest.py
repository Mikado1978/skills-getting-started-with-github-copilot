"""
Shared fixtures and configuration for FastAPI tests.

This module provides:
- TestClient fixture for API testing
- Sample activities data fixture
- Request builders for common test scenarios
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Provides a FastAPI TestClient for making requests to the app.
    
    Yields:
        TestClient: Client configured to test the FastAPI application.
    """
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """
    Provides a fresh copy of sample activities data.
    
    This fixture returns a deep copy of the activities dictionary to ensure
    test isolation. Each test receives its own independent copy, preventing
    cross-test pollution.
    
    Yields:
        dict: Sample activities with structure: {activity_name: {description, schedule, max_participants, participants}}
    """
    activities_data = {
        "Chess Club": {
            "description": "Learn and play chess",
            "schedule": "Monday & Thursday at 4:00 PM",
            "max_participants": 2,
            "participants": []
        },
        "Programming Class": {
            "description": "Learn Python programming",
            "schedule": "Tuesday & Friday at 3:30 PM",
            "max_participants": 20,
            "participants": []
        },
        "Gym Class": {
            "description": "Physical fitness training",
            "schedule": "Monday, Wednesday & Friday at 5:00 PM",
            "max_participants": 30,
            "participants": []
        },
        "Basketball Team": {
            "description": "Join our basketball team",
            "schedule": "Monday & Wednesday at 5:00 PM",
            "max_participants": 12,
            "participants": []
        },
        "Football Club": {
            "description": "Join our football club",
            "schedule": "Tuesday & Thursday at 4:00 PM",
            "max_participants": 22,
            "participants": []
        },
        "Art Club": {
            "description": "Explore your artistic side",
            "schedule": "Wednesday at 3:30 PM",
            "max_participants": 15,
            "participants": []
        },
        "Drama Club": {
            "description": "Act and perform on stage",
            "schedule": "Thursday at 3:30 PM",
            "max_participants": 10,
            "participants": []
        },
        "Debate Club": {
            "description": "Develop your debate skills",
            "schedule": "Friday at 4:00 PM",
            "max_participants": 8,
            "participants": []
        },
        "Science Club": {
            "description": "Conduct science experiments",
            "schedule": "Tuesday at 4:00 PM",
            "max_participants": 25,
            "participants": []
        }
    }
    return copy.deepcopy(activities_data)


@pytest.fixture
def sample_request_payload():
    """
    Provides a template for signup request payloads.
    
    Returns:
        dict: A sample request payload with email key.
    """
    return {"email": "student@example.com"}
