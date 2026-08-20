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


def test_missing_task_returns_404(client):
    assert client.get("/tasks/999").status_code == 404


def test_status_filter(client):
    client.post("/tasks", json={"title": "open one"})
    done_id = client.post("/tasks", json={"title": "done one"}).json()["id"]
    client.post(f"/tasks/{done_id}/complete")

    open_tasks = client.get("/tasks?status=open").json()
    assert [t["title"] for t in open_tasks] == ["open one"]


def test_search_matches_title(client):
    client.post("/tasks", json={"title": "Write demo script"})
    client.post("/tasks", json={"title": "Review pull request"})

    tasks = client.get("/tasks?q=demo").json()
    assert [t["title"] for t in tasks] == ["Write demo script"]


def test_search_matches_description(client):
    client.post(
        "/tasks",
        json={"title": "Docs", "description": "Explain the release process"},
    )
    client.post("/tasks", json={"title": "Tests", "description": "Add API coverage"})

    tasks = client.get("/tasks?q=release").json()
    assert [t["title"] for t in tasks] == ["Docs"]


def test_search_is_case_insensitive(client):
    client.post("/tasks", json={"title": "Ship Feature"})

    tasks = client.get("/tasks?q=feature").json()
    assert [t["title"] for t in tasks] == ["Ship Feature"]


def test_search_no_matches(client):
    client.post("/tasks", json={"title": "Write docs"})

    assert client.get("/tasks?q=missing").json() == []


def test_search_combines_with_status_filter(client):
    client.post("/tasks", json={"title": "Fix API bug"})
    done_id = client.post("/tasks", json={"title": "Fix UI bug"}).json()["id"]
    client.post(f"/tasks/{done_id}/complete")

    tasks = client.get("/tasks?status=open&q=fix").json()
    assert [t["title"] for t in tasks] == ["Fix API bug"]
