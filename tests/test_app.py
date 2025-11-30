"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""

    def test_get_activities(self):
        """Test that the /activities endpoint returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert len(activities) == 9

    def test_activity_structure(self):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]

        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_activity_has_valid_fields(self):
        """Test that all activities have required fields with valid types"""
        response = client.get("/activities")
        activities = response.json()
        for activity_name, activity in activities.items():
            assert isinstance(activity["description"], str)
            assert isinstance(activity["schedule"], str)
            assert isinstance(activity["max_participants"], int)
            assert isinstance(activity["participants"], list)


class TestSignupEndpoint:
    """Tests for the /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]

    def test_signup_already_registered(self):
        """Test that duplicate signup returns 400 error"""
        email = "duplicate@mergington.edu"
        # First signup
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        # Second signup with same email
        response = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self):
        """Test that signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_participant_added_to_activity(self):
        """Test that signup adds participant to activity"""
        email = "newparticipant@mergington.edu"
        response = client.post(
            f"/activities/Programming%20Class/signup?email={email}"
        )
        assert response.status_code == 200

        # Verify participant is in the activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Programming Class"]["participants"]

    def test_signup_multiple_activities(self):
        """Test that a student can signup for multiple activities"""
        email = "multiactivity@mergington.edu"
        activities = ["Chess Club", "Music Band", "Science Club"]
        for activity in activities:
            response = client.post(
                f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
            )
            assert response.status_code == 200


class TestUnregisterEndpoint:
    """Tests for the /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self):
        """Test successful unregister from an activity"""
        email = "unregister@mergington.edu"
        # First signup
        client.post(f"/activities/Art%20Studio/signup?email={email}")
        # Then unregister
        response = client.delete(
            f"/activities/Art%20Studio/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_not_registered(self):
        """Test that unregister for non-registered participant returns 400"""
        response = client.delete(
            "/activities/Tennis%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_nonexistent_activity(self):
        """Test that unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Fake%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_participant_removed_from_activity(self):
        """Test that unregister removes participant from activity"""
        email = "removeme@mergington.edu"
        # Signup
        client.post(f"/activities/Debate%20Team/signup?email={email}")
        # Unregister
        client.delete(f"/activities/Debate%20Team/unregister?email={email}")

        # Verify participant is removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities["Debate Team"]["participants"]


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirect(self):
        """Test that root redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
