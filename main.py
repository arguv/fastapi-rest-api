from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Task
from typing import Literal

app = FastAPI(title="Task Manager API")

DbSession = Annotated[Session, Depends(get_db)]


# Request schema
class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False
    priority: Literal["low", "medium", "high"] = "medium"


# Response schema
class TaskResponse(TaskCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "task-manager-api",
    }


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(task: TaskCreate, db: DbSession):
    new_task = Task(**task.model_dump())

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(db: DbSession):
    statement = select(Task).order_by(Task.id)
    return db.scalars(statement).all()


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: DbSession):
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskCreate, db: DbSession):
    existing_task = db.get(Task, task_id)

    if existing_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    for field, value in task.model_dump().items():
        setattr(existing_task, field, value)

    db.commit()
    db.refresh(existing_task)

    return existing_task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(task_id: int, db: DbSession):
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()