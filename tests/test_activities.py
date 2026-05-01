"""Tests for FastAPI activities endpoints."""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns status code 200."""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary of activities."""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)

    def test_get_activities_contains_all_activities(self, client):
        """Test that GET /activities returns all 9 expected activities."""
        response = client.get("/activities")
        data = response.json()
        assert len(data) == 9
        
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Drama Club",
            "Debate Team",
            "Science Club",
        ]
        
        for activity_name in expected_activities:
            assert activity_name in data

    def test_get_activities_response_structure(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        data = response.json()
        
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        for activity_name, activity in data.items():
            assert isinstance(activity_name, str)
            assert set(activity.keys()) == required_fields
            assert isinstance(activity["description"], str)
            assert isinstance(activity["schedule"], str)
            assert isinstance(activity["max_participants"], int)
            assert isinstance(activity["participants"], list)


class TestSignupActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "student@example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Chess Club" in data["message"]
        assert "student@example.com" in data["message"]

    def test_signup_adds_email_to_participants(self, client):
        """Test that signup adds email to activity's participants list."""
        email = "participant@test.com"
        
        # Get initial state
        initial = client.get("/activities").json()
        initial_count = len(initial["Chess Club"]["participants"])
        
        # Sign up
        client.post("/activities/Chess Club/signup", params={"email": email})
        
        # Verify participant was added
        updated = client.get("/activities").json()
        assert len(updated["Chess Club"]["participants"]) == initial_count + 1
        assert email in updated["Chess Club"]["participants"]

    def test_signup_duplicate_returns_400(self, client):
        """Test that duplicate signup returns 400 Bad Request."""
        email = "duplicate@example.com"
        
        # First signup succeeds
        response1 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup with same email fails
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "detail" in data
        assert "already" in data["detail"].lower()

    def test_signup_invalid_activity_returns_404(self, client):
        """Test that signup for non-existent activity returns 404."""
        response = client.post(
            "/activities/Non-Existent Activity/signup",
            params={"email": "student@example.com"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_signup_multiple_activities_same_email(self, client):
        """Test that a student can signup for multiple different activities."""
        email = "student@example.com"
        
        # Sign up for first activity
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify both signups succeeded
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Tennis Club"]["participants"]

    def test_signup_with_special_characters_in_email(self, client):
        """Test signup with special characters in email address."""
        email = "student+tag@example.co.uk"
        response = client.post(
            "/activities/Art Studio/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        activities = client.get("/activities").json()
        assert email in activities["Art Studio"]["participants"]

    def test_signup_activity_name_case_sensitive(self, client):
        """Test that activity name lookup is case-sensitive."""
        # Lowercase should fail
        response = client.post(
            "/activities/chess club/signup",
            params={"email": "student@example.com"}
        )
        assert response.status_code == 404

    def test_signup_whitespace_in_activity_name(self, client):
        """Test signup with activity name containing whitespace."""
        response = client.post(
            "/activities/Science Club/signup",
            params={"email": "science@example.com"}
        )
        assert response.status_code == 200
        assert "Science Club" in response.json()["message"]
