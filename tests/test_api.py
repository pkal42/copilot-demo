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


@pytest.mark.parametrize(
    ("sort", "order", "expected"),
    [
        ("created_at", "asc", ["Charlie", "alpha", "Bravo"]),
        ("created_at", "desc", ["Bravo", "alpha", "Charlie"]),
        ("title", "asc", ["alpha", "Bravo", "Charlie"]),
        ("title", "desc", ["Charlie", "Bravo", "alpha"]),
        ("priority", "asc", ["Bravo", "alpha", "Charlie"]),
        ("priority", "desc", ["Charlie", "alpha", "Bravo"]),
    ],
)
def test_sort_tasks(client, sort, order, expected):
    for title, priority in [
        ("Charlie", "low"),
        ("alpha", "medium"),
        ("Bravo", "high"),
    ]:
        client.post("/tasks", json={"title": title, "priority": priority})

    response = client.get(f"/tasks?sort={sort}&order={order}")

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == expected


def test_sort_tasks_with_status_and_search_filters(client):
    client.post("/tasks", json={"title": "Write report", "priority": "low"})
    done_id = client.post(
        "/tasks", json={"title": "Review report", "priority": "high"}
    ).json()["id"]
    client.post(f"/tasks/{done_id}/complete")
    client.post("/tasks", json={"title": "Review presentation", "priority": "medium"})

    response = client.get("/tasks?status=open&search=review&sort=title&order=desc")

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["Review presentation"]


@pytest.mark.parametrize(
    "query", ["sort=due_date", "order=sideways", "sort=title&order=sideways"]
)
def test_invalid_sort_parameters_return_422(client, query):
    response = client.get(f"/tasks?{query}")

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"].startswith("Input should be")
