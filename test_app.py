"""End-to-end tests for the Task Manager API using Flask's test client."""

import os
import tempfile

import database
from app import app


def setup_module():
    """Point the DB to a temp file and init it before tests."""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    database.DB_PATH = tmp.name
    tmp.close()
    database.init_db()


def test_lifecycle():
    client = app.test_client()

    # 1. Create a task
    r = client.post(
        "/tasks",
        json={"title": "Buy milk", "description": "Get 2% milk"},
    )
    assert r.status_code == 201, r.get_json()
    task = r.get_json()
    assert task["title"] == "Buy milk"
    assert task["description"] == "Get 2% milk"
    assert task["status"] == "pending"
    assert "id" in task and "created_at" in task
    task_id = task["id"]

    # 2. Get all tasks
    r = client.get("/tasks")
    assert r.status_code == 200
    tasks = r.get_json()
    assert any(t["id"] == task_id for t in tasks)

    # 3. Get one task
    r = client.get(f"/tasks/{task_id}")
    assert r.status_code == 200
    assert r.get_json()["id"] == task_id

    # 4. Update task (partial)
    r = client.put(f"/tasks/{task_id}", json={"status": "completed"})
    assert r.status_code == 200
    assert r.get_json()["status"] == "completed"
    assert r.get_json()["title"] == "Buy milk"

    # PATCH also works
    r = client.patch(f"/tasks/{task_id}", json={"title": "Buy 1% milk"})
    assert r.status_code == 200
    assert r.get_json()["title"] == "Buy 1% milk"

    # 5. Delete task
    r = client.delete(f"/tasks/{task_id}")
    assert r.status_code == 204

    # 6. Confirm deleted -> 404
    r = client.get(f"/tasks/{task_id}")
    assert r.status_code == 404
    assert r.get_json()["error"] == "Task not found"


def test_validation():
    client = app.test_client()

    # Missing title
    r = client.post("/tasks", json={})
    assert r.status_code == 400
    assert "Title is required" in r.get_json()["error"]

    # Whitespace title
    r = client.post("/tasks", json={"title": "   "})
    assert r.status_code == 400

    # Invalid status
    r = client.post(
        "/tasks", json={"title": "ok", "status": "in_progress"}
    )
    assert r.status_code == 400
    assert "Status must be" in r.get_json()["error"]

    # Malformed JSON
    r = client.post(
        "/tasks",
        data="{not json",
        content_type="application/json",
    )
    assert r.status_code == 400

    # PUT with blank title
    r = client.post("/tasks", json={"title": "temp"})
    tid = r.get_json()["id"]
    r = client.put(f"/tasks/{tid}", json={"title": "  "})
    assert r.status_code == 400
    client.delete(f"/tasks/{tid}")


def test_404s():
    client = app.test_client()

    # Unknown route
    r = client.get("/nope")
    assert r.status_code == 404

    # Update missing task
    r = client.put("/tasks/99999", json={"status": "completed"})
    assert r.status_code == 404
    assert r.get_json()["error"] == "Task not found"

    # Delete missing task
    r = client.delete("/tasks/99999")
    assert r.status_code == 404


if __name__ == "__main__":
    setup_module()
    test_lifecycle()
    test_validation()
    test_404s()
    print("All tests passed!")
