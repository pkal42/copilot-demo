from datetime import datetime, timezone
from typing import Literal, Optional

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

    def list(
        self,
        status: Optional[str] = None,
        search: Optional[str] = None,
        sort: Optional[Literal["created_at", "title", "priority"]] = None,
        order: Literal["asc", "desc"] = "asc",
    ) -> list[Task]:
        tasks = list(self._tasks.values())
        if status is not None:
            tasks = [task for task in tasks if task.status == status]
        if search is not None:
            query = search.casefold()
            tasks = [
                task
                for task in tasks
                if query in task.title.casefold() or query in task.description.casefold()
            ]
        if sort is not None:
            key = (
                (lambda task: task.created_at)
                if sort == "created_at"
                else (lambda task: task.title.casefold())
                if sort == "title"
                else lambda task: {"high": 0, "medium": 1, "low": 2}[task.priority]
            )
            tasks.sort(key=key, reverse=order == "desc")
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
