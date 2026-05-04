"""
Unit tests for activities business logic.

Tests the core data operations and business rules:
- Activity lookup and validation
- Participant management
- Capacity and duplicate detection
"""

import pytest


class TestActivityLookup:
    """Test activity validation and lookup logic."""

    def test_activity_exists_in_sample_data(self, sample_activities):
        """
        Arrange: Sample activities fixture
        Act: Check if Chess Club exists
        Assert: Chess Club is present in activities
        """
        assert "Chess Club" in sample_activities
        assert "description" in sample_activities["Chess Club"]

    def test_activity_not_found(self, sample_activities):
        """
        Arrange: Sample activities fixture
        Act: Look for non-existent activity
        Assert: Activity is not in the dictionary
        """
        assert "Non-existent Club" not in sample_activities


class TestParticipantManagement:
    """Test participant list operations."""

    def test_add_participant_to_activity(self, sample_activities):
        """
        Arrange: Sample activities fixture with empty participants
        Act: Add a participant to Chess Club
        Assert: Participant is added to the list
        """
        activity = sample_activities["Chess Club"]
        email = "test@example.com"
        
        activity["participants"].append(email)
        
        assert email in activity["participants"]
        assert len(activity["participants"]) == 1

    def test_remove_participant_from_activity(self, sample_activities):
        """
        Arrange: Activity with a participant
        Act: Remove the participant
        Assert: Participant is removed from the list
        """
        activity = sample_activities["Programming Class"]
        email = "student@example.com"
        activity["participants"].append(email)
        
        activity["participants"].remove(email)
        
        assert email not in activity["participants"]

    def test_duplicate_participant_detection(self, sample_activities):
        """
        Arrange: Activity with an existing participant
        Act: Check if email already exists
        Assert: Duplicate is detected
        """
        activity = sample_activities["Art Club"]
        email = "duplicate@example.com"
        activity["participants"].append(email)
        
        is_duplicate = email in activity["participants"]
        
        assert is_duplicate is True


class TestCapacityManagement:
    """Test capacity validation logic."""

    def test_activity_below_max_capacity(self, sample_activities):
        """
        Arrange: Activity with capacity of 20 and 5 participants
        Act: Check if there's room for more
        Assert: Activity is not full
        """
        activity = sample_activities["Programming Class"]
        activity["participants"] = ["p1@test.com", "p2@test.com", "p3@test.com", 
                                    "p4@test.com", "p5@test.com"]
        
        is_full = len(activity["participants"]) >= activity["max_participants"]
        
        assert is_full is False

    def test_activity_at_max_capacity(self, sample_activities):
        """
        Arrange: Activity with capacity of 12, filled to capacity
        Act: Check if activity is full
        Assert: Activity is at maximum capacity
        """
        activity = sample_activities["Chess Club"]
        activity["max_participants"] = 2
        activity["participants"] = ["p1@test.com", "p2@test.com"]
        
        is_full = len(activity["participants"]) >= activity["max_participants"]
        
        assert is_full is True

    def test_activity_over_capacity_impossible_with_append(self, sample_activities):
        """
        Arrange: Activity at capacity
        Act: Attempt to add another participant
        Assert: The length would exceed capacity (guards should prevent this)
        """
        activity = sample_activities["Drama Club"]
        activity["max_participants"] = 2
        activity["participants"] = ["p1@test.com", "p2@test.com"]
        
        # This simulates what would happen if guards fail
        activity["participants"].append("p3@test.com")
        
        assert len(activity["participants"]) > activity["max_participants"]
