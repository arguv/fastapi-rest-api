from fastapi import FastAPI, status
from pydantic import BaseModel


app = FastAPI(title="Task Manager API")


# Request schema
class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False


# Response schema
class TaskResponse(TaskCreate):
    id: int


# Temporary in-memory storage
tasks: dict[int, TaskResponse] = {}
next_task_id = 1


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "task-manager-api"
    }


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_task(task: TaskCreate):
    global next_task_id

    new_task = TaskResponse(
        id=next_task_id,
        **task.model_dump()
    )

    tasks[next_task_id] = new_task
    next_task_id += 1

    return new_task