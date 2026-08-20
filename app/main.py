from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app.models import Task, TaskCreate, store

app = FastAPI(title="Copilot Demo — Task Tracker", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tasks", response_model=list[Task])
def list_tasks(
    status: Optional[str] = None,
    search: Optional[str] = None,
    sort: Optional[Literal["created_at", "title", "priority"]] = None,
    order: Literal["asc", "desc"] = "asc",
) -> list[Task]:
    return store.list(status, search, sort, order)


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(payload: TaskCreate) -> Task:
    return store.add(payload)


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int) -> Task:
    task = store.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/tasks/{task_id}/complete", response_model=Task)
def complete_task(task_id: int) -> Task:
    task = store.complete(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    from pathlib import Path

    return Path(__file__).with_name("static").joinpath("index.html").read_text(
        encoding="utf-8"
    )
