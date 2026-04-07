# How the Project Works

A high-level walkthrough of what happens when a request reaches the server, and how the three main files connect to each other.

---

## The Request Lifecycle

Here's what happens when someone sends a request to create a task:

```
Client (browser, curl, Swagger UI)
  │
  │  POST /tasks  {"title": "Buy milk"}
  ▼
Uvicorn (web server)
  │  Receives the raw HTTP request
  │  Passes it to FastAPI
  ▼
FastAPI (framework) — main.py
  │  Looks at the URL (/tasks) and method (POST)
  │  Finds the matching endpoint function
  │  Validates the request body against the Pydantic model
  │  (If validation fails → returns 422 error, your function never runs)
  ▼
Router — app/routers/tasks.py
  │  create_task() runs
  │  Creates a TaskResponse with a new ID
  │  Appends it to the in-memory list
  │  Returns the new task
  ▼
FastAPI
  │  Converts the Python object to JSON
  │  Sends HTTP 201 response back
  ▼
Client
      Receives: {"id": 1, "title": "Buy milk", "description": "", "completed": false}
```

### In Plain English

1. **Client** sends an HTTP request (e.g., `POST /tasks` with a JSON body)
2. **Uvicorn** receives the raw request and hands it to FastAPI
3. **FastAPI** matches the URL + method to a function, then validates the request body using Pydantic models
4. **Your function** runs — does the actual work and returns a result
5. **FastAPI** converts the result to JSON and sends the HTTP response
6. **Client** receives the response

If validation fails at step 3 (bad data, missing fields), FastAPI returns a `422` error automatically — your function never executes.

---

## The Three Key Files

| File | Role | Analogy |
|------|------|---------|
| `main.py` | Creates the app, registers routers, defines `/health` | The front door — where everything starts |
| `app/models.py` | Defines what a Task looks like (fields, types, validation rules) | The blueprint — what data must look like |
| `app/routers/tasks.py` | Contains the endpoint functions (create, read, update, delete, search) | The workers — functions that do the actual work |

---

## How They Connect

```
main.py
  │
  ├── Creates the FastAPI app instance
  ├── Imports the tasks router from app/routers/tasks.py
  ├── Calls app.include_router(tasks.router) to register all /tasks/* endpoints
  └── Defines the /health endpoint directly (it's simple enough to live here)

app/routers/tasks.py
  │
  ├── Imports Task, TaskUpdate, TaskResponse from app/models.py
  ├── Uses Task to validate incoming POST request bodies
  ├── Uses TaskUpdate to validate incoming PUT request bodies
  └── Returns TaskResponse objects (FastAPI converts them to JSON automatically)

app/models.py
  │
  ├── Task         — input model for creating (title required, description optional)
  ├── TaskUpdate   — input model for updating (all fields optional)
  └── TaskResponse — output model (inherits from Task, adds the server-assigned id)
```

---

## Why Three Models?

You might wonder why we have `Task`, `TaskUpdate`, and `TaskResponse` instead of just one model. Each serves a different purpose:

| Model | Used For | Required Fields | Why It's Separate |
|-------|----------|----------------|------------------|
| `Task` | **Creating** a task (POST input) | `title` (required), `description` (optional), `completed` (optional) | The client shouldn't be able to set the `id` — the server assigns it |
| `TaskUpdate` | **Updating** a task (PUT input) | Everything optional | Partial updates — the client sends only the fields they want to change |
| `TaskResponse` | **Returning** a task (output) | All fields including `id` | The response includes the server-assigned `id` so the client knows it |

### The Inheritance

`TaskResponse` extends `Task` (notice `class TaskResponse(Task)` in the code). This means it automatically gets all of `Task`'s fields (title, description, completed) plus the new `id` field. If you add a field to `Task`, it automatically appears in `TaskResponse` too.

---

## Data Storage

Currently, tasks are stored in a plain Python list in `app/routers/tasks.py`:

```python
tasks = []      # In-memory storage — lost when the server restarts
next_id = 1     # Counter for assigning unique IDs
```

This means:
- **Data is lost** every time the server restarts
- **No persistence** between sessions
- **No concurrency safety** — fine for learning, not for production

In a real application, you'd replace this with a database (like PostgreSQL or SQLite). The endpoint functions would stay almost the same — only the storage logic would change.

---

## How FastAPI Auto-Generates Docs

FastAPI reads your code and automatically creates interactive documentation:

1. **Route decorators** (`@router.get`, `@router.post`) tell it what endpoints exist
2. **Type hints** (`task: Task`, `task_id: int`) tell it what the inputs look like
3. **Pydantic models** tell it the exact shape of request/response bodies
4. **Docstrings** become the description text in the docs
5. **`response_model`** tells it what the output looks like

All of this happens without you writing any documentation code. Visit `/docs` (Swagger UI) or `/redoc` (ReDoc) when the server is running to see it in action.

---

## What Happens on Errors

| Scenario | Who Handles It | HTTP Status | Example |
|----------|---------------|-------------|---------|
| URL doesn't match any endpoint | FastAPI | 404 | `GET /nonexistent` |
| Path parameter is the wrong type | FastAPI | 422 | `GET /tasks/abc` (expects int) |
| Request body fails validation | Pydantic via FastAPI | 422 | Missing `title` field |
| Your code raises `HTTPException` | Your code | Whatever you set | `raise HTTPException(status_code=404, ...)` |
| Your code raises an unexpected error | FastAPI | 500 | Unhandled Python exception |

FastAPI catches all of these and returns a properly formatted JSON error response. The server keeps running — it doesn't crash.
