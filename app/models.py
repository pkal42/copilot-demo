from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    priority: str = "medium"


class Task(BaseModel):
    id: int
    title: str
    description: str = ""
    priority: str = "medium"
    status: str = "open"
    created_at: datetime


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TaskStore:
    """In-memory store. Simple on purpose so demos stay fast."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1

    def add(self, payload: TaskCreate) -> Task:
        task = Task(
            id=self._next_id,
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            status="open",
            created_at=utcnow(),
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def list(self, status: Optional[str] = None, q: Optional[str] = None) -> list[Task]:
        tasks = list(self._tasks.values())
        if status is not None:
            tasks = [task for task in tasks if task.status == status]
        query = q.strip().casefold() if q is not None else ""
        if query:
            tasks = [
                task
                for task in tasks
                if query in task.title.casefold()
                or query in task.description.casefold()
            ]
        return tasks

    def get(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)

    def complete(self, task_id: int) -> Optional[Task]:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        task.status = "done"
        return task

    def clear(self) -> None:
        self._tasks.clear()
        self._next_id = 1


store = TaskStore()
