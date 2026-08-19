# GitHub Copilot — End-to-End Demo Script

**Duration:** ~20 minutes (or 8 min "lightning" — see the ⚡ markers)
**Repo:** `pkal42/copilot-demo`
**Story:** One small app, one backlog. Watch the same developer intent flow through
four Copilot surfaces — editor, terminal, desktop app, and the cloud.

---

## 0 · Setup (do this before the audience arrives)

```bash
git clone https://github.com/pkal42/copilot-demo
cd copilot-demo
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
pytest -q          # 4 pass, 1 xfail — the xfail is our planted bug
uvicorn app.main:app --reload
```

Have open and ready:
- VS Code on the repo, Copilot Chat panel visible
- A terminal with `copilot` (Copilot CLI) installed and authed
- The GitHub Copilot desktop app, `copilot-demo` added as a project
- A browser tab on `github.com/pkal42/copilot-demo/issues`
- Browser tab on `http://127.0.0.1:8000`

**Pre-file these four issues** (script in §5) so the Coding Agent demo is one click.

---

## 1 · Framing (90 seconds)

> "Copilot isn't one product — it's one model of collaboration that meets you
> wherever the work happens. I'm going to fix four things in this app, and I'll
> use a different Copilot surface for each. Same repo, same context, four modes
> of working: **synchronous in the editor**, **agentic in the terminal**,
> **orchestrated on the desktop**, and **autonomous in the cloud**."

Show the app at `localhost:8000`. Add a task. Click "Done". Click the "Open"
filter — **nothing changes.** That's bug #1.

Then point at `.github/copilot-instructions.md`:

> "One thing that makes all four surfaces good instead of generic: this file.
> Repo conventions, written once, respected everywhere."

---

## 2 · Copilot in the IDE ⚡ (4 minutes)
**Theme: tight feedback loop. You stay in flow, Copilot fills the gaps.**

### 2a. Inline completion (30s)
Open `app/models.py`. Below `complete()`, start typing:

```python
    def count_by_status(self) -> dict[str, int]:
```

Pause. Let the ghost text appear. Accept with Tab.

> "That's not autocomplete — it read my `TaskStore`, my type hints, my naming."

### 2b. Chat with `@workspace` grounding (60s)
In Copilot Chat:

```
@workspace The "Open" filter in the UI does nothing. Where does the status
filter get dropped?
```

It should point at `TaskStore.list()` in `app/models.py`.

> "It didn't grep for 'filter'. It reasoned across the route handler, the store,
> and the frontend fetch call to find where the value goes missing."

### 2c. Copilot Edits — multi-file fix (2 min)
Switch to **Edits** mode. Add `app/models.py` and `tests/test_api.py`. Prompt:

```
Fix the status filter in TaskStore.list so it filters by status when provided.
Then remove the xfail marker from test_status_filter in tests/test_api.py.
```

Review the diff **out loud** — this is the moment to model good behavior:

> "I read every line before I accept. That's the job now."

Accept. Run in the VS Code terminal:

```bash
pytest -q
```

5 passed. Refresh the browser, click "Open" — it works.

**Land the point:** *IDE = you're driving, Copilot is your co-pilot on a
30-second loop.*

---

## 3 · Copilot CLI (4 minutes)
**Theme: the terminal is a first-class agent surface. Multi-step, tool-using.**

> "Now I'm leaving the editor. Some work isn't editing — it's exploring,
> running, testing, committing. That's terminal work."

```bash
copilot
```

Prompt:

```
This API has no way to delete a task. Add DELETE /tasks/{id} following the
conventions in .github/copilot-instructions.md — logic in TaskStore, a 404 for
unknown ids, and a test. Add a delete button to the UI too. Run pytest when done.
```

While it works, narrate what you see:

> "Watch the tool calls. It's reading `models.py`, reading `main.py`, checking
> the instructions file, editing three files, then *running the tests itself*.
> That last part matters — it verifies before it claims success."

When it finishes:

```bash
git diff --stat
pytest -q
```

Then, still in the CLI:

```
Commit this on a branch called feat/delete-task and open a PR.
```

> "One session: explore, implement, test, branch, PR. No context switch, no
> copy-paste, and it never left the terminal."

**Land the point:** *CLI = agentic and headless-capable. It's the same agent you
can wire into scripts, hooks, and CI.*

---

## 4 · GitHub Copilot App (4 minutes)
**Theme: orchestration. Multiple isolated sessions, working in parallel.**

> "Everything so far was one task at a time. Real work isn't like that."

In the desktop app, with `copilot-demo` as the project, start a session in
**Plan mode**:

```
Add validation so tasks can't be created with an empty or whitespace-only title,
and cap the title at 120 characters. Return a clear 422. Include tests.
```

Show the **plan** before any code is written.

> "Plan mode is the guardrail. I approve the approach, *then* it writes code.
> This is where you catch a wrong turn for free instead of in review."

Approve it. While it runs, **start a second session in parallel**:

```
Add a GET /tasks/stats endpoint returning counts by status and by priority,
with tests.
```

Now show the sidebar with two sessions running.

> "Two agents, two isolated git worktrees, zero collisions. My working copy
> hasn't moved. This is the part people underestimate — the bottleneck stops
> being how fast Copilot writes code and becomes how fast I can review it."

Review one session's diff in the app, and merge/finish it.

**Land the point:** *App = the control plane. You go from writing code to
directing work.*

---

## 5 · Copilot Coding Agent (cloud) (4 minutes)
**Theme: fully autonomous. Delegate from anywhere, including your phone.**

Go to the Issues tab. Open the pre-filed issue:

> **Title:** Add optional due dates to tasks
> **Body:**
> Tasks should support an optional `due_date` (ISO 8601, nullable).
> - Accept it on `POST /tasks` and include it in all task responses
> - Add `GET /tasks?overdue=true` to return open tasks past their due date
> - Show the due date in the UI, highlighted red when overdue
> - Follow `.github/copilot-instructions.md`; add tests for every new behavior

Assign the issue to **Copilot**.

> "That's it. No terminal, no editor, no laptop required. It spins up its own
> cloud environment, clones the repo, reads the instructions file, and works."

Show a **previously completed** run so you're not waiting on stage — open the PR
it produced and walk through:
- The session log / progress timeline
- The diff, and the tests it added
- **CI green** on `.github/workflows/ci.yml`
- Leave a review comment: `Please also validate that due_date isn't in the past.`
- Show the agent pushing a follow-up commit in response

> "It responds to code review like a teammate. That's the loop that makes this
> trustworthy — not that it's always right, but that it's *correctable* through
> the exact process you already use."

**Land the point:** *Coding Agent = async delegation. Backlog work happens while
you're doing something else.*

---

## 6 · Close (90 seconds)

Put the four side by side:

| Surface | Latency | You are… | Best for |
| --- | --- | --- | --- |
| **IDE** | seconds | driving | the code in front of you |
| **CLI** | minutes | pairing | multi-step work in the terminal |
| **App** | minutes, parallel | directing | several tasks at once |
| **Coding Agent** | async | delegating | well-scoped backlog items |

> "Same repo, same instructions file, same review gate. What changes is how much
> you hand off and how long you're willing to wait. The skill you're building
> isn't prompting — it's **choosing the right surface for the task, and reviewing
> what comes back.**"

Final beat — the git log:

```bash
git log --oneline -8
```

> "Four surfaces. One history. Every change reviewed by a human."

---

## Appendix A · Lightning version (8 min)
Run only the ⚡ sections: §1 framing → §2b+§2c IDE fix → §3 CLI delete endpoint →
§5 with a pre-completed Coding Agent PR → §6 close.

## Appendix B · Failure recovery
- **Copilot suggests something wrong on stage?** *Lean in.* "Good — this is
  exactly why we review." Correct it with a follow-up prompt. It's the most
  credible moment in the whole demo.
- **Network dies?** Fall back to the pre-completed Coding Agent PR and the
  `git log`.
- **Tests fail unexpectedly?** `git stash` and rerun; the planted bug is the only
  intentional failure.

## Appendix C · Reset between runs

```bash
git checkout main && git reset --hard origin/main && git clean -fd
gh pr list --state open   # close any demo PRs
```
