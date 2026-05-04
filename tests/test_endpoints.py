"""
Integration tests for FastAPI endpoints.

Tests all HTTP endpoints with realistic payloads and scenarios:
- GET /activities - Retrieve all activities
- GET / - Root redirect
- POST /activities/{activity_name}/signup - Sign up for activity
- DELETE /activities/{activity_name}/participants - Remove participant
"""

import pytest
from fastapi import status


class TestGetActivitiesEndpoint:
    """Test GET /activities endpoint."""

    def test_get_activities_success(self, client):
        """
        Arrange: Make a GET request to /activities
        Act: Execute the request
        Assert: Returns 200 status and contains all activities
        """
        response = client.get("/activities")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9

    def test_get_activities_returns_activity_structure(self, client):
        """
        Arrange: Make a GET request to /activities
        Act: Execute the request
        Assert: Response contains proper activity structure
        """
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_get_activities_includes_participants(self, client):
        """
        Arrange: Chess Club has 2 initial participants
        Act: Get activities
        Assert: Participants list is returned
        """
        response = client.get("/activities")
        data = response.json()
        chess_activity = data["Chess Club"]
        
        assert len(chess_activity["participants"]) == 2
        assert "michael@mergington.edu" in chess_activity["participants"]


class TestRootEndpoint:
    """Test GET / endpoint."""

    def test_root_redirects_to_static(self, client):
        """
        Arrange: Make a GET request to /
        Act: Execute the request (follow_redirects=False to check redirect)
        Assert: Returns redirect status code
        """
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert "/static/index.html" in response.headers["location"]

    def test_root_redirect_location(self, client):
        """
        Arrange: Make a GET request to /
        Act: Execute request and check location header
        Assert: Redirects to correct static file
        """
        response = client.get("/", follow_redirects=False)
        
        assert response.headers["location"] == "/static/index.html"


class TestSignupEndpoint:
    """Test POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        """
        Arrange: Prepare signup request for existing activity
        Act: Send POST request with email
        Assert: Returns 200 and confirmation message
        """
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """
        Arrange: Activity with known participants
        Act: Sign up a new student
        Assert: Participant is added to the list
        """
        # First signup
        client.post(
            "/activities/Art Club/signup",
            params={"email": "artist@mergington.edu"}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        participants = response.json()["Art Club"]["participants"]
        
        assert "artist@mergington.edu" in participants

    def test_signup_nonexistent_activity(self, client):
        """
        Arrange: Nonexistent activity name
        Act: Send signup request
        Assert: Returns 404 error
        """
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_participant(self, client):
        """
        Arrange: Student already signed up for activity
        Act: Attempt to sign up again
        Assert: Returns 400 error with duplicate message
        """
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_missing_email_parameter(self, client):
        """
        Arrange: Signup request without email parameter
        Act: Send POST request
        Assert: Returns 422 validation error
        """
        response = client.post("/activities/Chess Club/signup")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_signup_at_capacity_acceptance(self, client):
        """
        Arrange: Activity with less than max capacity
        Act: Sign up multiple students until near capacity
        Assert: All signups are accepted
        """
        # Chess Club has max 12 participants and starts with 2
        for i in range(3):
            response = client.post(
                f"/activities/Chess Club/signup",
                params={"email": f"player{i}@mergington.edu"}
            )
            assert response.status_code == status.HTTP_200_OK

    def test_signup_multiple_activities(self, client):
        """
        Arrange: Same student signs up for multiple activities
        Act: Sign up for different activities
        Assert: Signup succeeds for each
        """
        email = "polymath@mergington.edu"
        
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        response2 = client.post(
            "/activities/Science Club/signup",
            params={"email": email}
        )
        
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK


class TestRemoveParticipantEndpoint:
    """Test DELETE /activities/{activity_name}/participants endpoint."""

    def test_remove_participant_success(self, client):
        """
        Arrange: Existing participant in activity
        Act: Send DELETE request to remove participant
        Assert: Returns 200 and confirmation message
        """
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": email}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "Removed" in data["message"]

    def test_remove_participant_from_activity(self, client):
        """
        Arrange: Participant in activity
        Act: Remove the participant
        Assert: Participant is no longer in the activity
        """
        # First add a participant
        email = "tester@mergington.edu"
        client.post(
            "/activities/Drama Club/signup",
            params={"email": email}
        )
        
        # Then remove the participant
        response = client.delete(
            "/activities/Drama Club/participants",
            params={"email": email}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify removal
        activities_response = client.get("/activities")
        participants = activities_response.json()["Drama Club"]["participants"]
        assert email not in participants

    def test_remove_from_nonexistent_activity(self, client):
        """
        Arrange: Nonexistent activity name
        Act: Send DELETE request
        Assert: Returns 404 error
        """
        response = client.delete(
            "/activities/Ghost Club/participants",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_remove_nonexistent_participant(self, client):
        """
        Arrange: Participant not in activity
        Act: Attempt to remove non-member
        Assert: Returns 404 error
        """
        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": "notamember@mergington.edu"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_remove_missing_email_parameter(self, client):
        """
        Arrange: DELETE request without email parameter
        Act: Send DELETE request
        Assert: Returns 422 validation error
        """
        response = client.delete("/activities/Chess Club/participants")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_remove_then_readd_participant(self, client):
        """
        Arrange: Participant in activity
        Act: Remove and then re-add the participant
        Assert: Both operations succeed
        """
        email = "changeable@mergington.edu"
        
        # Add participant
        response1 = client.post(
            "/activities/Debate Club/signup",
            params={"email": email}
        )
        assert response1.status_code == status.HTTP_200_OK
        
        # Remove participant
        response2 = client.delete(
            "/activities/Debate Club/participants",
            params={"email": email}
        )
        assert response2.status_code == status.HTTP_200_OK
        
        # Re-add participant (should succeed since already removed)
        response3 = client.post(
            "/activities/Debate Club/signup",
            params={"email": email}
        )
        assert response3.status_code == status.HTTP_200_OK


class TestActivityIntegrationScenarios:
    """Integration tests combining multiple endpoints."""

    def test_full_activity_lifecycle(self, client):
        """
        Arrange: Start with initial activities state
        Act: Get activities, sign up, remove, get again
        Assert: State changes are consistent across operations
        """
        email = "lifecycle@mergington.edu"
        
        # Step 1: Get initial state
        initial = client.get("/activities").json()
        initial_count = len(initial["Basketball Team"]["participants"])
        
        # Step 2: Sign up
        signup_response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": email}
        )
        assert signup_response.status_code == status.HTTP_200_OK
        
        # Step 3: Verify signup
        after_signup = client.get("/activities").json()
        assert len(after_signup["Basketball Team"]["participants"]) == initial_count + 1
        assert email in after_signup["Basketball Team"]["participants"]
        
        # Step 4: Remove
        remove_response = client.delete(
            "/activities/Basketball Team/participants",
            params={"email": email}
        )
        assert remove_response.status_code == status.HTTP_200_OK
        
        # Step 5: Verify removal
        after_removal = client.get("/activities").json()
        assert len(after_removal["Basketball Team"]["participants"]) == initial_count
        assert email not in after_removal["Basketball Team"]["participants"]

    def test_multiple_students_same_activity(self, client):
        """
        Arrange: Activity with available capacity
        Act: Multiple students sign up
        Assert: All signups succeed and all appear in participants
        """
        activity = "Football Club"
        emails = ["student1@test.com", "student2@test.com", "student3@test.com"]
        
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all are in the activity
        final_state = client.get("/activities").json()
        activity_participants = final_state[activity]["participants"]
        
        for email in emails:
            assert email in activity_participants
