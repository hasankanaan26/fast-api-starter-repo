# Project Structure

A map of every file and folder in the project, what it does, and where to look when you want to make changes.

---

## File Tree

```
TaskAssistant/
├── main.py                  # Entry point — creates the app, registers routers
├── app/                     # Application code
│   ├── models.py            # Pydantic models — Task, TaskUpdate, TaskResponse
│   └── routers/             # Endpoint groups (one file per resource)
│       └── tasks.py         # All /tasks endpoints (CRUD + search)
├── docs/                    # Documentation
│   ├── API.md               # Full API reference with curl examples
│   ├── DEBUGGING.md         # How to use the VS Code debugger
│   ├── DEPLOYMENT.md        # How to deploy to production
│   ├── DEVELOPMENT.md       # Local setup, dependencies, Docker builds
│   ├── GLOSSARY.md          # Definitions of key terms
│   ├── GIT.md               # Git basics for beginners
│   ├── HOW-IT-WORKS.md      # Architecture walkthrough
│   ├── PROJECT-STRUCTURE.md # You are here!
│   ├── TESTING.md           # How to write and run tests
│   └── TROUBLESHOOTING.md   # Common errors and fixes
├── .vscode/                 # VS Code configuration
│   └── launch.json          # Debug launch profiles (press F5 to start)
├── pyproject.toml           # Project metadata and dependency list
├── uv.lock                  # Exact pinned dependency versions (auto-generated)
├── .python-version          # Tells uv which Python version to use
├── Dockerfile               # Instructions to build a Docker container
├── .gitignore               # Files Git should ignore (.venv, __pycache__, etc.)
└── README.md                # Project overview and quick start
```

---

## File-by-File Breakdown

### Application Code

| File | Purpose |
|------|---------|
| **`main.py`** | The starting point of the app. Creates the FastAPI instance, registers the tasks router, and defines the `/health` endpoint. When you run `uvicorn main:app`, this is the file uvicorn loads. |
| **`app/models.py`** | Defines the data models using Pydantic. `Task` is for creating, `TaskUpdate` is for partial updates, `TaskResponse` is for API responses (includes the `id`). All validation rules (string length, required fields, defaults) live here. |
| **`app/routers/tasks.py`** | Contains all the `/tasks` endpoint functions: list, create, get, search, update, delete. Also contains the in-memory task storage (a Python list) and the ID counter. |

### Configuration Files

| File | Purpose |
|------|---------|
| **`pyproject.toml`** | Lists the project's metadata (name, version, description) and its dependencies (fastapi, uvicorn). This is what `uv sync` reads to know what packages to install. **Edit this when:** you need to add or change project metadata. Use `uv add package-name` to add dependencies (it updates this file automatically). |
| **`uv.lock`** | Auto-generated lockfile that pins exact versions of every dependency (and their sub-dependencies). Ensures everyone on the team gets identical packages. **Never edit this manually** — it's updated automatically when you run `uv add`, `uv remove`, or `uv lock`. |
| **`.python-version`** | Contains just a version number (e.g., `3.11`). Tells uv which Python version to download and use. |
| **`.gitignore`** | Lists files and folders that Git should NOT track: `.venv/` (huge, machine-specific), `__pycache__/` (compiled bytecode), `.env` (secrets). |

### Docker

| File | Purpose |
|------|---------|
| **`Dockerfile`** | A recipe for building a Docker container image. Each line is a step: start with a Python base image, install uv, copy the code, install dependencies, define the startup command. |

### VS Code

| File | Purpose |
|------|---------|
| **`.vscode/launch.json`** | Defines how VS Code runs and debugs the app. Contains three profiles: debug with reload, debug without reload, and debug the current file. Press `F5` to use these. |

---

## Where to Look When...

| You Want To... | Look In |
|----------------|---------|
| Add a new field to tasks (e.g., `priority`) | `app/models.py` — add the field to `Task`, `TaskUpdate`, and `TaskResponse` |
| Add a new endpoint (e.g., `GET /tasks/stats`) | `app/routers/tasks.py` — add a new function with a `@router.get()` decorator |
| Add a whole new resource (e.g., `/users`) | Create `app/routers/users.py` with its own router, then register it in `main.py` with `app.include_router()` |
| Change how the server starts | `main.py` for the app configuration, `.vscode/launch.json` for debug settings |
| Add a new Python package | Terminal: `uv add package-name` (updates `pyproject.toml` and `uv.lock` automatically) |
| Change which port the server runs on | The `--port` flag in the run command, or edit `.vscode/launch.json` |
| Ignore a new file type in Git | `.gitignore` — add a pattern like `*.log` or `data/` |
| Change the Python version | `.python-version` — change the number, then run `uv sync` |

---

## Folder Conventions

As the project grows, here's where new files should go:

| Type of File | Where It Goes |
|-------------|---------------|
| New API endpoints | `app/routers/new_resource.py` (one file per resource) |
| New data models | `app/models.py` (or split into `app/models/` if it gets too big) |
| Utility/helper functions | `app/utils.py` |
| Tests | `tests/test_*.py` |
| Documentation | `docs/` |
| Configuration | Project root (`.env`, `pyproject.toml`, etc.) |
