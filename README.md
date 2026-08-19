# Copilot Demo — Task Tracker API

A deliberately small FastAPI app used to demo **GitHub Copilot across all four surfaces**:

| Surface | What it shows |
| --- | --- |
| **Copilot in the IDE** (VS Code) | Inline completions, Chat, Agent mode, `@workspace` grounding |
| **Copilot CLI** | Terminal-native agent: explore, fix, test, commit |
| **GitHub Copilot App** | Multi-session orchestration, planning, parallel worktrees |
| **Copilot Coding Agent** (cloud) | Assign an issue → agent opens a PR autonomously |

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 for the UI, http://127.0.0.1:8000/docs for the API.

## Tests

```bash
pytest -q
```

## Demo script

See [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md) for the full 20-minute walkthrough.

## Intentional gaps (demo fuel)

These are left in on purpose — each one is fixed live by a different Copilot surface:

1. `GET /tasks?status=` filter ignores the `status` query param (bug) → **IDE**
2. No `DELETE /tasks/{id}` endpoint (missing feature) → **CLI**
3. No input validation on `title` (empty titles allowed) → **App**
4. No due-date support and no README badge / CI workflow → **Coding Agent**
