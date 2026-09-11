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


def test_reopen_completed_task(client):
    task_id = client.post("/tasks", json={"title": "Ship it"}).json()["id"]
    client.post(f"/tasks/{task_id}/complete")
    assert client.post(f"/tasks/{task_id}/reopen").json()["status"] == "open"


def test_reopen_open_task(client):
    task_id = client.post("/tasks", json={"title": "Still open"}).json()["id"]
    assert client.post(f"/tasks/{task_id}/reopen").json()["status"] == "open"


def test_reopen_missing_task_returns_404(client):
    assert client.post("/tasks/999/reopen").status_code == 404


def test_task_stats(client):
    open_id = client.post("/tasks", json={"title": "open"}).json()["id"]
    done_id = client.post("/tasks", json={"title": "done"}).json()["id"]
    client.post(f"/tasks/{done_id}/complete")

    assert client.get("/tasks/stats").json() == {"open": 1, "done": 1, "total": 2}

    client.post(f"/tasks/{open_id}/complete")
    client.post(f"/tasks/{open_id}/reopen")
    assert client.get("/tasks/stats").json() == {"open": 1, "done": 1, "total": 2}


def test_missing_task_returns_404(client):
    assert client.get("/tasks/999").status_code == 404


@pytest.mark.xfail(reason="Demo bug #1: status filter is not applied yet")
def test_status_filter(client):
    client.post("/tasks", json={"title": "open one"})
    done_id = client.post("/tasks", json={"title": "done one"}).json()["id"]
    client.post(f"/tasks/{done_id}/complete")

    open_tasks = client.get("/tasks?status=open").json()
    assert [t["title"] for t in open_tasks] == ["open one"]
