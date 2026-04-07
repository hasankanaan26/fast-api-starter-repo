# Development Guide

This guide is for project maintainers — setting up the project locally, managing dependencies, and building with Docker.

---

## Install uv (One-Time Setup)

uv is the tool that manages Python, packages, and virtual environments for this project. It is installed **globally on your system** (not inside a virtual environment) — think of it like Git or Docker: a tool you install once and use across all your projects.

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installing, **restart your terminal** (close and reopen it), then verify it works:

```bash
uv --version
# Should print something like: uv 0.6.x
```

> **Do NOT install uv with `pip install uv`** — that would install it inside a virtual environment, which defeats the purpose. uv manages virtual environments, so it needs to live outside of them. Use the install commands above instead.

> **Do NOT install Python separately** — uv downloads and manages the correct Python version automatically based on the `.python-version` file in the project.

---

## Local Setup from Scratch

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/TaskAssistant.git
cd TaskAssistant

# 2. Install dependencies and create the virtual environment
#    "uv sync" does everything in one step:
#      - Creates a .venv virtual environment (if it doesn't exist)
#      - Reads pyproject.toml to know what packages are needed
#      - Reads uv.lock to install the exact pinned versions
#      - Installs the project itself in editable mode
#    This replaces the old workflow of: python -m venv .venv → activate → pip install
uv sync

# 3. (Optional) Create a .env file for environment variables
#    This project doesn't require any env variables right now,
#    but if you add database URLs or API keys later, put them here.

# 4. Run the development server
#    "uv run" runs a command using the project's virtual environment.
#    You don't need to manually activate the .venv — uv handles it for you.
#    --reload makes the server restart automatically when you change code.
#    This is great for development but should NOT be used in production.
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API is now running at `http://localhost:8000`.  
Interactive docs are at `http://localhost:8000/docs` (Swagger UI).

---

## Managing Dependencies

```bash
# Add a new package — installs it AND updates pyproject.toml + uv.lock automatically.
# Your teammates will get the exact same version when they run "uv sync".
uv add some-package

# Remove a package:
uv remove some-package

# Update all dependencies to their latest compatible versions:
uv lock --upgrade
uv sync
```

> **Never use `pip install` directly** — it won't update `pyproject.toml` or `uv.lock`, so your changes won't be shared with the team.

---

## Build & Run with Docker Locally

```bash
# 1. Make sure Docker Desktop is running on your machine

# 2. Build the Docker image
#    -t gives the image a name ("tag") so you can refer to it easily later.
#    The "." at the end tells Docker to look for the Dockerfile in the current directory.
docker build -t task-assistant .

# 3. Run the container
#    -d = run in the background ("detached mode") so your terminal stays usable
#    -p 8000:8000 = map port 8000 on your machine to port 8000 inside the container
#    --name = give the running container a friendly name
docker run -d -p 8000:8000 --name task-assistant-app task-assistant

# 4. Check that it's running
docker ps

# 5. View logs (useful for debugging)
docker logs task-assistant-app

# 6. Stop and remove when you're done
docker stop task-assistant-app
docker rm task-assistant-app
```

---

## Gotchas & Common Mistakes

| Mistake | What Happens | Fix |
|---------|-------------|-----|
| Running `uvicorn` directly instead of `uv run uvicorn` | `ModuleNotFoundError` — your shell can't find packages in the .venv | Always use `uv run` to run commands, or activate the venv first |
| Running `uvicorn app:main` instead of `uvicorn main:app` | `Error loading ASGI app` | Format is `file_name:variable_name` — our file is `main.py`, the app variable is `app` |
| Port 8000 already in use | `Address already in use` | Kill the other process, or use a different port: `--port 8001` |
| Using `pip install` instead of `uv add` | Package installs but isn't tracked in pyproject.toml or uv.lock | Always use `uv add package-name` |
| Docker build fails on Windows | Line ending issues | Use LF line endings, not CRLF. Configure Git: `git config core.autocrlf input` |
