# API Reference

Full reference for every endpoint in the Task Assistant API.  
All examples use `curl`, but you can also use the interactive docs at `http://localhost:8000/docs`.

> **What is curl?** `curl` is a command-line tool that sends HTTP requests — it's like a browser, but in your terminal. If you're on Windows and don't have curl, you can paste the URLs directly into your browser for GET requests, or use the Swagger UI at `/docs`.

---

## Base URL

```
http://localhost:8000
```

---

## Endpoints

### Health Check

Check if the server is running.

```
GET /health
```

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{"status": "ok", "checkpoint": 1}
```

---

### List All Tasks

Get every task currently stored.

```
GET /tasks
```

```bash
curl http://localhost:8000/tasks
```

**Response** (empty):
```json
[]
```

**Response** (with tasks):
```json
[
  {
    "title": "Learn FastAPI",
    "description": "Build my first API project",
    "completed": false,
    "id": 1
  },
  {
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": true,
    "id": 2
  }
]
```

---

### Create a Task

Create a new task. The server assigns an ID automatically.

```
POST /tasks
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Task name (1–100 characters) |
| `description` | string | No | Additional details (max 500 characters, defaults to `""`) |
| `completed` | boolean | No | Whether the task is done (defaults to `false`) |

```bash
# Create a basic task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "description": "Build my first API project"}'
```

**Response** (`201 Created`):
```json
{
  "title": "Learn FastAPI",
  "description": "Build my first API project",
  "completed": false,
  "id": 1
}
```

**Validation errors:**
```bash
# Empty title → 422 error
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": ""}'

# Missing title entirely → 422 error
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"description": "no title provided"}'
```

---

### Get a Single Task

Get a specific task by its ID.

```
GET /tasks/{task_id}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_id` | int | The task's unique ID (from the URL path) |

```bash
curl http://localhost:8000/tasks/1
```

**Response:**
```json
{
  "title": "Learn FastAPI",
  "description": "Build my first API project",
  "completed": false,
  "id": 1
}
```

**Error** (task doesn't exist):
```json
{"detail": "Task 99 not found"}
```

---

### Search Tasks

Search for tasks by keyword in the title or description. The search is case-insensitive.

```
GET /tasks/search/?q={query}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search keyword |

```bash
# Search for tasks containing "FastAPI"
curl "http://localhost:8000/tasks/search/?q=FastAPI"
```

**Response:**
```json
[
  {
    "title": "Learn FastAPI",
    "description": "Build my first API project",
    "completed": false,
    "id": 1
  }
]
```

**No matches:**
```json
[]
```

---

### Update a Task

Update one or more fields of an existing task. Only include the fields you want to change — omitted fields keep their current values.

```
PUT /tasks/{task_id}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_id` | int | The task's unique ID (from the URL path) |

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | No | New title (1–100 characters) |
| `description` | string | No | New description (max 500 characters) |
| `completed` | boolean | No | New completed status |

```bash
# Mark a task as completed (without changing the title or description)
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

**Response:**
```json
{
  "title": "Learn FastAPI",
  "description": "Build my first API project",
  "completed": true,
  "id": 1
}
```

```bash
# Update multiple fields at once
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Master FastAPI", "completed": true}'
```

---

### Delete a Task

Delete a task by its ID. Returns the deleted task data for confirmation.

```
DELETE /tasks/{task_id}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_id` | int | The task's unique ID (from the URL path) |

```bash
curl -X DELETE http://localhost:8000/tasks/1
```

**Response:**
```json
{
  "message": "Task 1 deleted successfully",
  "task": {
    "title": "Learn FastAPI",
    "description": "Build my first API project",
    "completed": true,
    "id": 1
  }
}
```

**Error** (task doesn't exist):
```json
{"detail": "Task 1 not found"}
```

---

## Interactive API Docs

FastAPI automatically generates interactive documentation. Once the server is running, open:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs) — click-to-test interface
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc) — read-only reference format
