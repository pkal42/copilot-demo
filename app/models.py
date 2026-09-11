from datetime import datetime, timezone
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, StringConstraints, field_validator


TaskTitle = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)
]
TaskPriority = Literal["low", "medium", "high"]


class TaskCreate(BaseModel):
    title: TaskTitle
    description: str = ""
    priority: TaskPriority = "medium"


class TaskUpdate(BaseModel):
    title: Optional[TaskTitle] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None

    @field_validator("title", "description", "priority", mode="before")
    @classmethod
    def reject_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("Field cannot be null")
        return value


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

    def update(self, task_id: int, payload: TaskUpdate) -> Optional[Task]:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        return task

    def list(self, status: Optional[str] = None) -> list[Task]:
        # BUG (demo #1): the status filter is accepted but never applied.
        return list(self._tasks.values())

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
