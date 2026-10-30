from fastapi import FastAPI, HTTPException, status
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

@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks():
    return list(tasks.values())


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    global next_task_id

    new_task = TaskResponse(
        id=next_task_id,
        **task.model_dump()
    )

    tasks[next_task_id] = new_task
    next_task_id += 1

    return new_task

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    task = tasks.get(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskCreate):
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    updated_task = TaskResponse(
        id=task_id,
        **task.model_dump()
    )

    tasks[task_id] = updated_task

    return updated_task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    del tasks[task_id]
