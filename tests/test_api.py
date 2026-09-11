import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import store


@pytest.fixture(autouse=True)
def clean_store():
    store.clear()
    yield
    store.clear()


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_get_task(client):
    r = client.post("/tasks", json={"title": "Write demo script"})
    assert r.status_code == 201
    task_id = r.json()["id"]

    got = client.get(f"/tasks/{task_id}").json()
    assert got["title"] == "Write demo script"
    assert got["status"] == "open"


def test_complete_task(client):
    task_id = client.post("/tasks", json={"title": "Ship it"}).json()["id"]
    assert client.post(f"/tasks/{task_id}/complete").json()["status"] == "done"


def test_update_task_preserves_unspecified_fields(client):
    task = client.post(
        "/tasks",
        json={
            "title": "Original title",
            "description": "Original description",
            "priority": "low",
        },
    ).json()

    response = client.patch(
        f"/tasks/{task['id']}",
        json={"title": "Updated title"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"
    assert response.json()["description"] == "Original description"
    assert response.json()["priority"] == "low"


def test_update_task_description_and_priority(client):
    task_id = client.post("/tasks", json={"title": "Update me"}).json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"description": "New description", "priority": "high"},
    )

    assert response.status_code == 200
    assert response.json()["description"] == "New description"
    assert response.json()["priority"] == "high"


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "   "},
        {"title": "x" * 121},
        {"priority": "urgent"},
        {"description": None},
    ],
)
def test_update_task_rejects_invalid_input(client, payload):
    task_id = client.post("/tasks", json={"title": "Valid task"}).json()["id"]

    assert client.patch(f"/tasks/{task_id}", json=payload).status_code == 422


@pytest.mark.parametrize("title", ["   ", "x" * 121])
def test_create_task_reuses_title_constraints(client, title):
    assert client.post("/tasks", json={"title": title}).status_code == 422


def test_update_missing_task_returns_404(client):
    response = client.patch("/tasks/999", json={"title": "Missing"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_missing_task_returns_404(client):
    assert client.get("/tasks/999").status_code == 404


@pytest.mark.xfail(reason="Demo bug #1: status filter is not applied yet")
def test_status_filter(client):
    client.post("/tasks", json={"title": "open one"})
    done_id = client.post("/tasks", json={"title": "done one"}).json()["id"]
    client.post(f"/tasks/{done_id}/complete")

    open_tasks = client.get("/tasks?status=open").json()
    assert [t["title"] for t in open_tasks] == ["open one"]
