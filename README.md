# Task Manager API

A FastAPI service for creating and managing tasks. Tasks are persisted in PostgreSQL using SQLAlchemy, and the database schema is managed with Alembic migrations.

## Requirements

- Python 3.10 or newer
- Docker and Docker Compose (for the local PostgreSQL database)
- Dependencies listed in [`requirements.txt`](requirements.txt)

## Setup

Create and activate a virtual environment, then install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\\Scripts\\activate`.

Start PostgreSQL with Docker Compose:

```bash
cp .env.example .env
docker compose up -d db
```

Edit `.env` before starting the database and use a strong local password. The database is available on `localhost:5432` with the configured credentials:

| Setting | Value |
| --- | --- |
| Database | `task_manager` |
| User | `task_user` |
| Password | The value configured in `.env` |

Apply the schema migrations:

```bash
alembic upgrade head
```

## Run the API

```bash
uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Interactive documentation is available at `http://127.0.0.1:8000/docs`.

To stop PostgreSQL:

```bash
docker compose down
```

Use `docker compose down -v` when the local database volume should also be removed.

## API endpoints

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
  -d '{"title":"Learn FastAPI","description":"Build a task API","completed":false,"priority":"high"}'
```

The `title` field is required. `description` defaults to `null`, `completed` defaults to `false`, and `priority` defaults to `medium`. Valid priorities are `low`, `medium`, and `high`. New tasks receive an integer `id`. Requests for a missing task return HTTP 404; successful deletion returns HTTP 204.

## Database migrations

Create a new migration after changing the SQLAlchemy models:

```bash
alembic revision --autogenerate -m "describe the change"
```

Apply pending migrations with `alembic upgrade head` and roll back one migration with:

```bash
alembic downgrade -1
```

The application uses the connection configured through the environment variables in `.env`. Alembic can be pointed at another database with the `ALEMBIC_DATABASE_URL` environment variable.

## Running tests

The test suite uses a separate PostgreSQL database named `task_manager_test`. Create it once in the local PostgreSQL container:

```bash
docker exec -it fastapi-postgres psql -U task_user -d task_manager -c 'CREATE DATABASE task_manager_test;'
```

Then run the tests:

```bash
python -m pytest -v
```

Tests create and remove their tables automatically and do not require the API server to be running.
