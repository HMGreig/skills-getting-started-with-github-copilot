"""
Tests for the Mergington High School Activities API
"""

import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from fastapi.testclient import TestClient
from app import app, activities

# Create a test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Save original state
    original_activities = {
        "Basketball": {
            "description": "Team sport focusing on skills, strategy, and fitness",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Individual and doubles tennis matches and training",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["james@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["maya@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Learn instruments and perform in concerts",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "isabella@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 14,
            "participants": ["grace@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design and build robots for competitions",
            "schedule": "Tuesdays, Thursdays, Saturdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["ryan@mergington.edu", "noah@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(original_activities)
    yield
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    def test_get_activities_success(self):
        """Test that we can retrieve all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Basketball" in data
        assert "Tennis Club" in data

    def test_get_activities_contains_required_fields(self):
        """Test that activities contain required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Basketball"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_get_activities_participants_list(self):
        """Test that participants are properly listed"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Basketball"]
        
        assert isinstance(activity["participants"], list)
        assert "alex@mergington.edu" in activity["participants"]


class TestSignup:
    def test_signup_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Basketball"]["participants"]

    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/NonExistentActivity/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_student(self):
        """Test that a student cannot sign up twice for the same activity"""
        response = client.post(
            "/activities/Basketball/signup?email=alex@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_multiple_students(self):
        """Test that multiple students can sign up for the same activity"""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        response1 = client.post(f"/activities/Basketball/signup?email={email1}")
        response2 = client.post(f"/activities/Basketball/signup?email={email2}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both were added
        activities_response = client.get("/activities")
        participants = activities_response.json()["Basketball"]["participants"]
        assert email1 in participants
        assert email2 in participants

    def test_signup_at_capacity(self):
        """Test that students can still signup even if activity appears full"""
        # Note: Based on current implementation, there's no capacity check
        # This test documents current behavior
        response = client.post(
            "/activities/Chess Club/signup?email=overcapacity@mergington.edu"
        )
        assert response.status_code == 200


class TestUnregister:
    def test_unregister_success(self):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Basketball/unregister?email=alex@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        participants = activities_response.json()["Basketball"]["participants"]
        assert "alex@mergington.edu" not in participants

    def test_unregister_activity_not_found(self):
        """Test unregister for non-existent activity"""
        response = client.delete(
            "/activities/NonExistentActivity/unregister?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_student_not_signed_up(self):
        """Test unregister for student who is not signed up"""
        response = client.delete(
            "/activities/Basketball/unregister?email=notstudent@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_multiple_students(self):
        """Test unregistering multiple students from the same activity"""
        response1 = client.delete(
            "/activities/Music Ensemble/unregister?email=lucas@mergington.edu"
        )
        response2 = client.delete(
            "/activities/Music Ensemble/unregister?email=isabella@mergington.edu"
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both were removed
        activities_response = client.get("/activities")
        participants = activities_response.json()["Music Ensemble"]["participants"]
        assert len(participants) == 0


class TestIntegration:
    def test_signup_and_unregister_flow(self):
        """Test a complete flow: signup and then unregister"""
        email = "integration@mergington.edu"
        
        # Sign up
        signup_response = client.post(
            f"/activities/Tennis Club/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        participants = activities_response.json()["Tennis Club"]["participants"]
        assert email in participants
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/Tennis Club/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        final_response = client.get("/activities")
        final_participants = final_response.json()["Tennis Club"]["participants"]
        assert email not in final_participants

    def test_root_redirect(self):
        """Test that root path redirects to static files"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
