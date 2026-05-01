"""Test configuration and shared fixtures for FastAPI backend tests."""

import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


# Store the initial state of activities for resetting between tests
INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Fixture that resets activities to initial state before each test.
    This ensures test isolation and prevents state leakage between tests.
    """
    # Reset activities to initial state
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    # Clean up after test (optional, but good practice)
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient instance for making requests to the FastAPI app.
    Each test gets a fresh client with reset activities data (via reset_activities fixture).
    """
    return TestClient(app)
