from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def setup_function():
    # Reset in-memory activities for each test
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        }
    })


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_signup_new_participant():
    payload = {"email": "sophia@mergington.edu"}
    response = client.post("/activities/Chess Club/signup", params=payload)
    assert response.status_code == 200
    assert "Signed up sophia@mergington.edu for Chess Club" in response.json()["message"]

    data = client.get("/activities").json()
    assert "sophia@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_existing_participant_rejected():
    response = client.post("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant():
    response = client.delete("/activities/Chess Club/participants", params={"email": "Daniel@mergington.edu"})
    assert response.status_code == 404  # case-sensitive check for missing participant

    response = client.delete("/activities/Chess Club/participants", params={"email": "daniel@mergington.edu"})
    assert response.status_code == 200
    assert response.json()["message"] == "Removed daniel@mergington.edu from Chess Club"

    data = client.get("/activities").json()
    assert "daniel@mergington.edu" not in data["Chess Club"]["participants"]
