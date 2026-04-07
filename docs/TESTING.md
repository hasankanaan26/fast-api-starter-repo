# Testing Guide

Testing means writing code that automatically checks whether your code works correctly — instead of manually testing every endpoint by hand after every change.

---

## Why Test?

- You change `create_task()` and accidentally break `search_tasks()`. Without tests, you won't notice until someone reports it. With tests, you find out in seconds.
- Tests let you refactor code confidently — if the tests pass, you haven't broken anything.
- Tests serve as living documentation — they show exactly how each function is supposed to behave.

---

## Setting Up pytest

```bash
# Install pytest (the most popular Python test framework) and httpx (for testing FastAPI)
uv add --dev pytest httpx

# --dev means it's a development dependency — it won't be included when deploying to production.
# httpx is needed because FastAPI's test client uses it under the hood to send fake HTTP requests.
```

---

## Writing Your First Test

Create a folder called `tests/` and a file inside it called `test_tasks.py`:

```python
"""
Tests for the Task Assistant API.

Each test function:
  1. Sends a request to the API (using a fake client, no real server needed)
  2. Checks that the response is what we expected

If the check fails, pytest tells you exactly what went wrong.
"""

from fastapi.testclient import TestClient
from main import app

# TestClient lets us send fake HTTP requests to the app
# without starting a real server. It's fast and works in memory.
client = TestClient(app)


def test_health_check():
    """The /health endpoint should return status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_task():
    """Creating a task should return 201 with the task data including an id."""
    response = client.post("/tasks", json={
        "title": "Test task",
        "description": "A task created by a test"
    })
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Test task"
    assert data["description"] == "A task created by a test"
    assert data["completed"] is False
    assert "id" in data  # The server should assign an ID


def test_create_task_without_title():
    """Creating a task without a title should return 422 (validation error)."""
    response = client.post("/tasks", json={
        "description": "Missing the title"
    })
    assert response.status_code == 422


def test_get_nonexistent_task():
    """Requesting a task ID that doesn't exist should return 404."""
    response = client.get("/tasks/99999")
    assert response.status_code == 404
```

### Understanding the Pattern

Every test follows the same three-step pattern:

1. **Arrange** — Set up what you need (in our case, the `client` is already set up)
2. **Act** — Do the thing you're testing (`client.post(...)`, `client.get(...)`)
3. **Assert** — Check the result (`assert response.status_code == 201`)

### What Does `assert` Do?

`assert` checks that something is true. If it is, nothing happens and the test continues. If it's false, the test fails immediately and pytest shows you what the actual value was.

```python
assert 1 + 1 == 2      # Passes (nothing happens)
assert 1 + 1 == 3      # Fails! pytest shows: "assert 2 == 3"
```

---

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output (shows each test name and its result)
uv run pytest -v

# Run a specific test file
uv run pytest tests/test_tasks.py

# Run a specific test function
uv run pytest tests/test_tasks.py::test_create_task

# Stop on the first failure (useful when fixing a bug — don't drown in errors)
uv run pytest -x

# Show print() output (normally pytest hides it)
uv run pytest -s
```

---

## Reading Test Output

### All Tests Pass

```
$ uv run pytest -v
========================= test session starts =========================
tests/test_tasks.py::test_health_check PASSED                    [ 25%]
tests/test_tasks.py::test_create_task PASSED                     [ 50%]
tests/test_tasks.py::test_create_task_without_title PASSED       [ 75%]
tests/test_tasks.py::test_get_nonexistent_task PASSED            [100%]
========================= 4 passed in 0.15s ===========================
```

### A Test Fails

```
FAILED tests/test_tasks.py::test_create_task
    assert data["completed"] is True
    AssertionError: assert False is True
```

Read the error **bottom-up**:
1. `assert False is True` — the actual value was `False`, but the test expected `True`
2. `data["completed"] is True` — the line of code that failed
3. `test_create_task` — the test function that failed

### What Each Result Means

| Result | Meaning |
|--------|---------|
| **PASSED** | The test worked as expected |
| **FAILED** | An `assert` statement was false — something didn't match expectations |
| **ERROR** | The test itself crashed before it could check anything (usually an import error or typo) |
| **SKIPPED** | The test was intentionally skipped (not relevant here, but you'll see it in larger projects) |

---

## What to Test

For each endpoint, test:

1. **The happy path** — Does it work with valid input?
2. **Validation errors** — Does it reject bad input? (missing fields, wrong types)
3. **Not found** — Does it return 404 for IDs that don't exist?
4. **Edge cases** — Empty strings, very long strings, special characters

For this project, good tests to write:

| Test | What It Checks |
|------|---------------|
| Create a task with all fields | POST works with valid data |
| Create a task with only a title | Optional fields default correctly |
| Create a task with no title | Returns 422 |
| Create a task with an empty title | Returns 422 (whitespace-only titles are stripped then rejected) |
| Get a task that exists | Returns the correct task |
| Get a task that doesn't exist | Returns 404 |
| List tasks when none exist | Returns an empty list |
| List tasks after creating some | Returns all created tasks |
| Update a task (partial) | Only the specified fields change |
| Update a nonexistent task | Returns 404 |
| Delete a task | Returns the deleted task |
| Delete a nonexistent task | Returns 404 |
| Search with a matching query | Returns matching tasks |
| Search with no matches | Returns an empty list |

---

## Test Naming Conventions

pytest discovers tests automatically based on naming:

- **Test files:** Must start with `test_` (e.g., `test_tasks.py`, `test_models.py`)
- **Test functions:** Must start with `test_` (e.g., `test_create_task`)
- **Test folder:** Usually called `tests/`

Be descriptive in your test names. They show up in the output when tests fail:

```python
# Bad — tells you nothing when it fails
def test_error():

# Good — immediately tells you what broke
def test_create_task_without_title_returns_422():
```

---

## Running Tests in VS Code

1. Open the **Testing** sidebar (flask icon in the left bar, or `Ctrl+Shift+P` > "Testing: Focus on Test Explorer View")
2. VS Code should auto-discover your tests
3. Click the play button next to a test to run it
4. Click the play button at the top to run all tests
5. Failed tests show a red X — click to see the error

You can also **debug a test**: right-click a test in the Test Explorer and select "Debug Test". This lets you set breakpoints inside your test code or inside your API code, and step through line by line.
