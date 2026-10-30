# Task Manager API In Python

A small FastAPI service for creating and managing tasks. Tasks are stored in memory and are lost when the server restarts.

To run the automated tests, see [Running tests](#running-tests).

## Requirements

- Python 3.10 or newer
- Dependencies listed in `requirements.txt` (including FastAPI, Uvicorn, pytest, and HTTPX)

## Setup and run

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

On Windows, activate the environment with `.venv\Scripts\activate`.

The API is available at `http://127.0.0.1:8000`. Interactive API documentation is at `http://127.0.0.1:8000/docs`.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Check service health |
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create a task |
| GET | `/tasks/{task_id}` | Get a task by ID |
| PUT | `/tasks/{task_id}` | Replace a task by ID |
| DELETE | `/tasks/{task_id}` | Delete a task by ID |

Create a task:

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"Learn FastAPI","description":"Build a task API","completed":false}'
```

`title` is required. `description` defaults to `null`, and `completed` defaults to `false`. New tasks receive an integer `id`. Requests for a missing task return HTTP 404; successful deletion returns HTTP 204.

## Running tests

From the project directory, create and activate a virtual environment if you have not already done so:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies from `requirements.txt` if you have not already done so, then run the full test suite:

```bash
python -m pip install -r requirements.txt
python -m pytest -v
```

On Windows, activate the environment with `.venv\Scripts\activate` before running the `python` commands. The tests use FastAPI's `TestClient`, so the API server does not need to be running. They cover the health endpoint, task creation and listing, fetching a task, and the 404 response for a missing task.
