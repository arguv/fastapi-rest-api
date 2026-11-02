import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from database import get_db
from main import app
from models import Base

TEST_DATABASE_URL = (
    "postgresql+psycopg://"
    f"{os.getenv('POSTGRES_USER', 'task_user')}:"
    f"{os.getenv('POSTGRES_PASSWORD', '')}@"
    f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
    f"{os.getenv('POSTGRES_PORT', '5432')}/"
    f"{os.getenv('POSTGRES_TEST_DB', 'task_manager_test')}"
)

test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    def override_get_db():
        with TestingSessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_task(client):
    response = client.post(
        "/tasks",
        json={"title": "Learn Python"},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["title"] == "Learn Python"
    assert data["completed"] is False


def test_list_tasks(client):
    client.post(
        "/tasks",
        json={"title": "Learn FastAPI"},
    )

    response = client.get("/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_task(client):
    client.post(
        "/tasks",
        json={"title": "Learn pytest"},
    )

    response = client.get("/tasks/1")

    assert response.status_code == 200
    assert response.json()["title"] == "Learn pytest"


def test_get_nonexistent_task(client):
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_create_task_with_high_priority(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Important task",
            "priority": "high",
        },
    )

    assert response.status_code == 201
    assert response.json()["priority"] == "high"


def test_create_task_with_default_priority(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Normal task",
        },
    )

    assert response.status_code == 201
    assert response.json()["priority"] == "medium"


def test_create_task_with_invalid_priority(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Invalid task",
            "priority": "urgent",
        },
    )

    assert response.status_code == 422


def test_get_task_with_priority(client):
    create_response = client.post(
        "/tasks",
        json={
            "title": "Read priority",
            "priority": "low",
        },
    )

    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["priority"] == "low"
