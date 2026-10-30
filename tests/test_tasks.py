import pytest
from fastapi.testclient import TestClient

from main import app, tasks


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_tasks():
    tasks.clear()

    import main
    main.next_task_id = 1

    yield

    tasks.clear()


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_task():
    response = client.post(
        "/tasks",
        json={"title": "Learn Python"}
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["title"] == "Learn Python"
    assert data["completed"] is False


def test_list_tasks():
    client.post(
        "/tasks",
        json={"title": "Learn FastAPI"}
    )

    response = client.get("/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_task():
    client.post(
        "/tasks",
        json={"title": "Learn pytest"}
    )

    response = client.get("/tasks/1")

    assert response.status_code == 200
    assert response.json()["title"] == "Learn pytest"


def test_get_nonexistent_task():
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"