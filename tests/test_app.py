from fastapi.testclient import TestClient
import uuid

from src.app import app


client = TestClient(app)


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # Basic sanity: expected activity present
    assert "Chess Club" in data


def test_signup_and_remove_participant_flow():
    # Use a unique email to avoid collisions with existing in-memory data
    email = f"test-{uuid.uuid4().hex}@example.com"
    activity = "Basketball Club"

    # Ensure the email is not already in the participants list
    before = client.get("/activities").json()
    assert email not in before[activity]["participants"]

    # Sign up
    signup_res = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup_res.status_code == 200
    assert "Signed up" in signup_res.json().get("message", "")

    # Confirm participant appears
    after = client.get("/activities").json()
    assert email in after[activity]["participants"]

    # Try signing up the same email again -> should fail with 400
    dup_res = client.post(f"/activities/{activity}/signup?email={email}")
    assert dup_res.status_code == 400

    # Remove the participant
    del_res = client.delete(f"/activities/{activity}/participants?email={email}")
    assert del_res.status_code == 200
    assert "Removed" in del_res.json().get("message", "")

    # Confirm removal
    final = client.get("/activities").json()
    assert email not in final[activity]["participants"]


def test_remove_nonexistent_participant_returns_404():
    email = f"noone-{uuid.uuid4().hex}@example.com"
    activity = "Math Club"

    res = client.delete(f"/activities/{activity}/participants?email={email}")
    assert res.status_code == 404
