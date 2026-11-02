# Task Manager API

A FastAPI service for creating and managing tasks. Tasks are persisted in PostgreSQL using SQLAlchemy, and the database schema is managed with Alembic migrations.

## Requirements

- Python 3.10 or newer
- Docker and Docker Compose (for the local PostgreSQL database)
- Dependencies listed in [`requirements.txt`](requirements.txt)

## Setup

Copy the environment template and set a strong local database password:

```bash
cp .env.example .env
```

The database is available on `localhost:5432` with the credentials configured in `.env`:

| Setting | Value |
| --- | --- |
| Database | `task_manager` |
| User | `task_user` |
| Password | The value configured in `.env` |

## Run the full stack with Docker

Build the FastAPI image and start both the API and PostgreSQL containers:

```bash
docker compose config
docker compose build api
docker compose up -d
```

The API is available at `http://127.0.0.1:8000`. Interactive documentation is available at `http://127.0.0.1:8000/docs`.

Apply the schema migrations inside the API container:

```bash
docker compose exec api alembic upgrade head
```

Check the services and API health:

```bash
docker compose ps
curl -i http://127.0.0.1:8000/health
```

Check the database connection from the API container:

```bash
docker compose exec api python -c "from database import check_database_connection; print(check_database_connection())"
```

Open a PostgreSQL shell from the database container:

```bash
docker compose exec db psql -U task_user -d task_manager
```

Restart one service without removing containers or volumes:

```bash
docker compose restart api
docker compose restart db
```

Expected output:

```text
('task_manager', 'task_user')
```

After changing application code or dependencies, rebuild and recreate the API container:

```bash
docker compose up -d --build --force-recreate api
```

View container logs or open a shell inside the API container:

```bash
docker compose logs -f api
docker compose logs -f db
docker compose exec api sh
```

To stop the stack while preserving the PostgreSQL volume:

```bash
docker compose stop
```

To remove the containers and network while preserving database data:

```bash
docker compose down
```

To remove the containers and permanently delete the named PostgreSQL volume and its data:

```bash
docker compose down -v
```

## Run the API locally

For local FastAPI development, start only PostgreSQL:

```bash
docker compose up -d db
```

Then create a virtual environment and install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\\Scripts\\activate`. Apply migrations and run the API from the project directory:

```bash
alembic upgrade head
uvicorn main:app --reload
```

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

When running the API locally, apply pending migrations with `alembic upgrade head` and roll back one migration with:

```bash
alembic downgrade -1
```

When running in Docker, use the same commands through the API container:

```bash
docker compose exec api alembic current
docker compose exec api alembic upgrade head
docker compose exec api alembic downgrade -1
```

The application uses `DATABASE_URL` inside Docker and the variables in `.env` locally. Alembic can be pointed at another database with the `ALEMBIC_DATABASE_URL` environment variable.

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
