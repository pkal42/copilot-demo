# Copilot instructions — Task Tracker

## Project
FastAPI task-tracker API plus a single-file HTML/JS UI. Storage is an in-memory
`TaskStore` in `app/models.py`. There is no database and none should be added.

## Layout
- `app/main.py` — routes only; keep handlers thin
- `app/models.py` — Pydantic models and `TaskStore` business logic
- `app/static/index.html` — the entire UI (no build step, no framework)
- `tests/test_api.py` — pytest + `fastapi.testclient`

## Conventions
- Python 3.12, full type hints on public functions
- Business logic belongs in `TaskStore`, not in route handlers
- Every new endpoint needs a test in `tests/test_api.py`
- Return `HTTPException(404, "Task not found")` for unknown task ids
- Keep the UI dependency-free — vanilla JS only

## Validation
Run `pytest -q` before proposing a change as complete.
