from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def activities_state(monkeypatch):
    state = deepcopy(app_module.activities)
    monkeypatch.setattr(app_module, "activities", state)
    return state


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_get_activities_returns_all_activities(client, activities_state):
    # Arrange
    expected_activities = deepcopy(activities_state)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_student_to_activity(client, activities_state):
    # Arrange
    activity_name = "Basketball Team"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in activities_state[activity_name]["participants"]


def test_signup_rejects_duplicate_student_without_changing_participants(
    client, activities_state
):
    # Arrange
    activity_name = "Chess Club"
    email = activities_state[activity_name]["participants"][0]
    original_participants = activities_state[activity_name]["participants"].copy()

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up"}
    assert activities_state[activity_name]["participants"] == original_participants


def test_signup_returns_not_found_for_unknown_activity(client, activities_state):
    # Arrange
    activity_name = "Unknown Activity"
    email = "new.student@mergington.edu"
    original_activities = deepcopy(activities_state)

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activities_state == original_activities


def test_unregister_removes_student_from_activity(client, activities_state):
    # Arrange
    activity_name = "Basketball Team"
    email = "student.to.remove@mergington.edu"
    activities_state[activity_name]["participants"].append(email)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert email not in activities_state[activity_name]["participants"]


def test_unregister_returns_not_found_for_unknown_student(client, activities_state):
    # Arrange
    activity_name = "Basketball Team"
    email = "not.registered@mergington.edu"
    original_participants = activities_state[activity_name]["participants"].copy()

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up"}
    assert activities_state[activity_name]["participants"] == original_participants


def test_unregister_returns_not_found_for_unknown_activity(
    client, activities_state
):
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"
    original_activities = deepcopy(activities_state)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activities_state == original_activities
