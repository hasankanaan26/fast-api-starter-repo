# Troubleshooting

Common errors you'll encounter and how to fix them. Organized by category so you can jump to the right section.

---

## Setup & Installation

| Error | Cause | Fix |
|-------|-------|-----|
| `uv: command not found` | uv isn't installed | Install it — Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` / Mac/Linux: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| `ModuleNotFoundError: No module named 'fastapi'` | Packages aren't installed, or you're not using the virtual environment | Run `uv sync`, then use `uv run uvicorn ...` instead of `uvicorn ...` directly |
| `error: Python 3.11 not found` | uv can't find the right Python version | Run `uv python install 3.11` — uv downloads it for you |
| VS Code shows import errors (red squiggles) but the code runs fine | VS Code is using the wrong Python interpreter | `Ctrl+Shift+P` > "Python: Select Interpreter" > choose the one in `.venv` |
| `running scripts is disabled on this system` (Windows) | PowerShell execution policy is too strict | Run: `Set-ExecutionPolicy -ExecutionPolicy ByPass -Scope CurrentUser` |

---

## Running the Server

| Error | Cause | Fix |
|-------|-------|-----|
| `Address already in use` (port 8000) | Another process is already using that port | Either stop the other process (check your terminal tabs — do you have a server running?), or use a different port: `--port 8001` |
| `Error loading ASGI app. Could not import module "app"` | Wrong module path in the run command | The correct command is `uvicorn main:app` (not `uvicorn app:main`). Format is `file_name:variable_name`. |
| `Error loading ASGI app. Attribute "app" not found in module "main"` | The variable name doesn't match | Check that `main.py` has a variable called `app` — e.g., `app = FastAPI(...)` |
| Server starts but all requests return 404 | The router isn't registered | Check that `main.py` has `app.include_router(tasks.router)` |
| `--reload` doesn't detect file changes | File watcher issue (common on some Windows setups) | Stop the server (`Ctrl+C`) and restart it manually, or try: `uv run uvicorn main:app --reload --reload-dir .` |

---

## Git

| Error | Cause | Fix |
|-------|-------|-----|
| `fatal: not a git repository` | You're not inside the project folder, or Git wasn't initialized | `cd` into the TaskAssistant folder. If there's no `.git` folder, run `git init`. |
| `error: failed to push some refs` | Someone else pushed changes you don't have yet | Run `git pull origin main` first, resolve any conflicts, then push again |
| `CONFLICT (content): Merge conflict in file.py` | Two people edited the same lines | Open the file, look for `<<<<<<<` markers, choose the correct version, then `git add` + `git commit`. See [GIT.md](GIT.md) for details. |
| `Your branch is behind 'origin/main' by 3 commits` | The remote has newer changes | Run `git pull origin main` to catch up |
| Accidentally committed to `main` instead of a branch | Forgot to create a branch before committing | Run `git checkout -b feature/my-work` to move your commit to a new branch. Then ask a teammate for help resetting `main`. |
| `fatal: remote origin already exists` | You tried to add a remote that's already configured | This is fine — run `git remote -v` to see what's already set up |

---

## Docker

| Error | Cause | Fix |
|-------|-------|-----|
| `Cannot connect to the Docker daemon` | Docker Desktop isn't running | Open Docker Desktop and wait for it to fully start (the whale icon in the system tray should stop animating) |
| `docker build` fails with "file not found" | You're not in the project root directory | Make sure you `cd TaskAssistant` before running `docker build .` |
| Container starts but can't connect on `localhost:8000` | Port mapping is missing | Run with `-p 8000:8000`: `docker run -d -p 8000:8000 task-assistant` |
| `exec format error` | Image was built for a different CPU architecture | Rebuild: `docker build --platform linux/amd64 -t task-assistant .` |
| `docker build` is very slow | No layer caching, or downloading packages every time | Make sure the Dockerfile copies `pyproject.toml` and `uv.lock` BEFORE copying the app code. Our Dockerfile already does this. |

---

## Debugging

| Problem | Cause | Fix |
|---------|-------|-----|
| Breakpoints aren't being hit | The `--reload` flag creates a child process and the debugger attaches to the wrong one | Use the "Debug: FastAPI (no reload)" launch profile. See [DEBUGGING.md](DEBUGGING.md). |
| Debugger starts but the server doesn't respond to requests | The debugger is paused on a breakpoint or exception | Check VS Code — is it showing a yellow highlighted line? Press `F5` to continue. |
| Can't find the Debug sidebar | It's collapsed or hidden | Press `Ctrl+Shift+D`, or click the play-with-bug icon in the left sidebar |
| `ModuleNotFoundError` when starting the debugger | VS Code is using the wrong Python interpreter | `Ctrl+Shift+P` > "Python: Select Interpreter" > choose the one in `.venv` |

---

## Python Errors

| Error | What It Means | Fix |
|-------|---------------|-----|
| `IndentationError: unexpected indent` | Mixed tabs and spaces, or wrong indentation level | In VS Code: `Ctrl+Shift+P` > "Convert Indentation to Spaces". Use 4 spaces per indent level. |
| `NameError: name 'x' is not defined` | Typo in a variable name, or using a variable before creating it | Check the spelling. Check that the variable is defined above the line that uses it. |
| `TypeError: 'NoneType' object is not subscriptable` | Trying to do `something["key"]` when `something` is `None` | The variable doesn't have a value. Use the debugger to check where it became `None`. |
| `ImportError: cannot import name 'X' from 'Y'` | The name doesn't exist in that module | Check the module — did you spell it correctly? Did you save the file after adding the definition? |
| `AttributeError: 'X' object has no attribute 'Y'` | You're trying to access a property or method that doesn't exist on the object | Check the class definition — is the attribute name spelled correctly? Is the object the type you think it is? |
| `SyntaxError: invalid syntax` | A typo in your Python code (missing colon, unmatched parenthesis, etc.) | Look at the line number in the error. Common causes: missing `:` after `if`/`for`/`def`, unclosed `(` or `[` on the previous line. |

---

## API Errors

| Status Code | What It Means | Common Cause |
|-------------|---------------|-------------|
| **404 Not Found** | The URL doesn't match any endpoint, or the task ID doesn't exist | Check the URL for typos. Check that the task ID is correct. |
| **405 Method Not Allowed** | The URL exists but not for that HTTP method | You sent `GET` to a `POST`-only endpoint (or vice versa). Check the method. |
| **422 Unprocessable Entity** | The request body failed validation | Missing required field (`title`), wrong type (string instead of int), or field too long. Read the error detail — it tells you exactly which field failed and why. |
| **500 Internal Server Error** | Something crashed in your code | Check the terminal where the server is running — the full error traceback is printed there. |

---

## Still Stuck?

1. **Read the error message carefully.** Python error messages are usually very descriptive. Read from the bottom up — the last line is the actual error, the lines above show where it happened.
2. **Search the error message.** Copy the error text (without your specific file paths) and search online. Someone else has almost certainly hit the same issue.
3. **Use the debugger.** Set a breakpoint just before the error happens and inspect the variables. See [DEBUGGING.md](DEBUGGING.md).
4. **Ask for help.** Include: what you're trying to do, the full error message, and what you've already tried.
