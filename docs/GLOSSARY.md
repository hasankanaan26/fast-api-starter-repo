# Glossary

Definitions of terms you'll encounter in the code, docs, and conversations about this project. Come back here whenever you hit a word you don't recognize.

---

## API & Web Concepts

| Term | Definition |
|------|-----------|
| **API** | Application Programming Interface — a way for programs to talk to each other over the network. This project IS an API: other programs send it HTTP requests, and it sends back JSON data. Think of it like a waiter — you tell the waiter what you want, and they bring it back from the kitchen. |
| **REST** | A style of designing APIs around "resources" and HTTP methods. Instead of calling functions like `createTask()`, you send `POST /tasks`. Instead of `getTask(5)`, you send `GET /tasks/5`. It's a convention, not a technology. |
| **CRUD** | Create, Read, Update, Delete — the four basic operations you can do with data. Almost every API and database app is built around CRUD. |
| **Endpoint** | A specific URL + HTTP method that does something. `GET /tasks` is one endpoint, `POST /tasks` is another, `DELETE /tasks/1` is another. |
| **HTTP** | HyperText Transfer Protocol — the language that web browsers and servers use to communicate. Every time you visit a website, your browser sends an HTTP request and gets an HTTP response back. |
| **HTTP Method** | The "verb" in an HTTP request: `GET` (read data), `POST` (create data), `PUT` (update data), `DELETE` (remove data). |
| **Status Code** | A number in every HTTP response that says what happened. The important ones: `200` = OK, `201` = Created, `404` = Not Found, `422` = Bad Input, `500` = Server Error. |
| **JSON** | JavaScript Object Notation — the data format APIs use to send and receive data. Looks like: `{"title": "Buy milk", "completed": false}`. Python dictionaries look almost identical. |
| **Request Body** | The data a client sends WITH a request (used in POST and PUT). For example, the JSON containing the new task's title and description. GET and DELETE requests usually don't have a body. |
| **Path Parameter** | A value embedded in the URL itself. In `/tasks/3`, the `3` is a path parameter representing the task ID. The server extracts it from the URL. |
| **Query Parameter** | A value appended to the URL after a `?`. In `/tasks/search/?q=milk`, `q=milk` is a query parameter. Used for optional filters and search queries. |
| **Header** | Metadata sent with an HTTP request or response. `Content-Type: application/json` tells the server "I'm sending JSON." You usually don't deal with headers directly — FastAPI handles them. |
| **Swagger UI** | An interactive web page that auto-documents your API. FastAPI generates it automatically at `/docs`. You can test every endpoint directly from your browser — no curl or Postman needed. |

---

## Python & FastAPI

| Term | Definition |
|------|-----------|
| **FastAPI** | The Python web framework this project uses. It handles routing (matching URLs to functions), validation (checking input data), serialization (converting Python objects to JSON), and auto-generates API docs. |
| **Uvicorn** | The web server that actually runs the FastAPI app. FastAPI defines *what* to do; uvicorn handles the *listening for requests* part. Think of uvicorn as the engine and FastAPI as the steering wheel. |
| **Pydantic** | A Python library for data validation. You define a model (like `Task`), and Pydantic automatically checks that incoming data matches — correct types, required fields present, strings not too long, etc. FastAPI uses Pydantic internally. |
| **Model** (Pydantic) | A Python class that defines the shape of data — what fields it has, what types they must be, and what the defaults are. Example: the `Task` model says a task must have a `title` (string, required) and `completed` (boolean, defaults to False). |
| **Router** | A group of related endpoints bundled together. Our `tasks.py` file creates a router that handles all `/tasks/*` endpoints. Routers keep code organized — one file per resource instead of one giant file. |
| **Decorator** | The `@something` lines above functions in Python. They modify the function's behavior. `@router.get("/tasks")` tells FastAPI "when someone sends a GET request to /tasks, call this function." |
| **Type Hint** | The `: int` or `: str` annotations after variable names. Example: `task_id: int` tells Python (and FastAPI) that this variable should be an integer. FastAPI uses these to auto-validate and auto-document. |
| **Virtual Environment** (venv) | An isolated folder containing Python packages for this project only. Prevents conflicts between projects that need different versions of the same package. `uv sync` creates and manages this in the `.venv` folder. |

---

## Tools

| Term | Definition |
|------|-----------|
| **uv** | A fast, modern Python package manager that replaces pip, pip-tools, and virtualenv. It manages Python versions, creates virtual environments, and installs packages — all in one tool. |
| **pip** | The traditional Python package installer. We use `uv` instead because it's faster and does more, but you'll see `pip` mentioned in tutorials and Stack Overflow posts everywhere. |
| **Git** | A version control system that tracks changes to your files over time. Like an unlimited undo system that also lets multiple people work on the same code. See [GIT.md](GIT.md). |
| **GitHub** | A website that hosts Git repositories online and adds collaboration features (pull requests, issues, code review). Git is the tool; GitHub is the platform. |
| **Docker** | A tool that packages your app and everything it needs (Python, packages, config) into a "container" — a lightweight, portable box that runs the same way everywhere. |
| **curl** | A command-line tool for sending HTTP requests. `curl http://localhost:8000/tasks` sends a GET request. It's like a browser, but in your terminal. |
| **pytest** | The most popular Python testing framework. You write test functions, and pytest automatically finds and runs them. See [TESTING.md](TESTING.md). |

---

## Git Concepts

| Term | Definition |
|------|-----------|
| **Repository (repo)** | A project folder tracked by Git. The hidden `.git` folder inside stores the full history of every change ever made. |
| **Commit** | A snapshot of your code at a point in time, with a message describing what changed. Like a save point in a video game. |
| **Branch** | A separate line of development. You create a branch to work on a feature, then merge it back into `main` when done. This keeps the main code stable while you experiment. |
| **Main / Master** | The primary branch — the "official" version of the code. All feature branches eventually merge back into `main`. |
| **Staging Area** | A holding area for changes you want in your next commit. `git add file.py` stages a file; `git commit` saves all staged changes. |
| **Remote** | The copy of your repo on GitHub. Your local copy and the remote stay in sync via `git push` (upload) and `git pull` (download). |
| **Pull Request (PR)** | A request to merge your branch into `main` on GitHub. Your team reviews the code changes before approving the merge. |
| **Merge Conflict** | When Git can't automatically combine changes because two people edited the same lines. You have to manually choose which version to keep. |
| **Clone** | Downloading a repository from GitHub to your computer for the first time: `git clone URL`. |

---

## File Types

| File | What It Is |
|------|-----------|
| **`.py`** | A Python source code file. |
| **`.md`** | A Markdown file — formatted text with headers, lists, tables, and code blocks. All the documentation files use Markdown. |
| **`.json`** | A JSON file — structured data in key-value format. `.vscode/launch.json` is a config file in JSON format. |
| **`.toml`** | A configuration file format (Tom's Obvious Minimal Language). `pyproject.toml` uses this format. |
| **`.lock`** | A lockfile that pins exact dependency versions. `uv.lock` ensures everyone installs identical packages. |
| **`.gitignore`** | A special file that tells Git which files/folders to NOT track (like `.venv/` and `__pycache__/`). |
| **`Dockerfile`** | Instructions for Docker to build a container image. No file extension — it's just called `Dockerfile`. |
