"""
Task router — defines all API endpoints for managing tasks.

This is the core of the application. It defines the CRUD (Create, Read, Update, Delete)
operations for tasks, plus a search endpoint. Each function handles a specific type of
HTTP request (GET, POST, PUT, DELETE) to a specific URL path.

How it works:
    - This file uses an APIRouter (like a mini FastAPI app) to group related endpoints
    - The router is registered in main.py with app.include_router()
    - All endpoints here are prefixed with "/tasks" (set in the router configuration)
    - Tasks are stored in an in-memory list (they reset when the server restarts)

Endpoints defined here:
    GET    /tasks            — List all tasks
    POST   /tasks            — Create a new task
    GET    /tasks/{task_id}  — Get a specific task by ID
    GET    /tasks/search/    — Search tasks by keyword
    PUT    /tasks/{task_id}  — Update a task
    DELETE /tasks/{task_id}  — Delete a task
"""

from fastapi import APIRouter, HTTPException, Query
from app.models import Task, TaskUpdate, TaskResponse

# Create a router instance.
# - prefix="/tasks": All routes in this file will start with /tasks
#   (so @router.get("") becomes GET /tasks, @router.get("/{task_id}") becomes GET /tasks/123)
# - tags=["tasks"]: Groups these endpoints together in the auto-generated docs at /docs
router = APIRouter(prefix="/tasks", tags=["tasks"])

# In-memory storage for tasks.
# This is a simple Python list that acts as our "database".
# WARNING: This data is lost when the server restarts! For a real app, you'd use
# a database like PostgreSQL or SQLite instead.
tasks = []

# Counter to assign unique IDs to each new task.
# Every time a task is created, this number increases by 1, ensuring no two tasks share an ID.
next_id = 1


# The @router.get("") decorator tells FastAPI:
# "When someone sends a GET request to /tasks, run this function."
# - response_model=list[TaskResponse]: Tells FastAPI what the response looks like.
#   FastAPI uses this to validate the response and generate documentation.
@router.get("", response_model=list[TaskResponse])
def list_tasks():
    """
    List all tasks.

    Returns every task currently stored in memory. If no tasks have been created yet,
    returns an empty list.

    Returns:
        list[TaskResponse]: A JSON array of all tasks, each with id, title,
                            description, and completed status.

    Example response:
        [
            {"id": 1, "title": "Buy milk", "description": "2% milk", "completed": false},
            {"id": 2, "title": "Walk dog", "description": "30 min walk", "completed": true}
        ]
    """
    return tasks


# @router.post("") handles POST requests to /tasks (for creating new resources).
# - status_code=201: Returns HTTP 201 "Created" instead of the default 200 "OK".
#   This follows REST conventions — 201 means "a new resource was successfully created."
@router.post("", response_model=TaskResponse, status_code=201)
def create_task(task: Task):
    """
    Create a new task.

    Takes a Task object from the request body (FastAPI automatically parses the JSON
    and validates it against the Task model), assigns it a unique ID, stores it in memory,
    and returns the complete task with its new ID.

    Args:
        task (Task): The task data sent by the client in the request body.
                     Must include "title" and "description". "completed" is optional
                     and defaults to False.

    Returns:
        TaskResponse: The newly created task, now including its server-assigned ID.

    Example:
        Request body: {"title": "Study", "description": "Chapter 3"}
        Response:     {"id": 1, "title": "Study", "description": "Chapter 3", "completed": false}
    """
    # "global" tells Python that "next_id" refers to the variable defined at the top
    # of this file, not a new local variable inside this function.
    # Without "global", Python would think we're creating a new variable and would
    # throw an error when we try to read its value before assigning it.
    global next_id

    # Create a TaskResponse (which includes the ID) from the incoming Task data
    new_task = TaskResponse(
        id=next_id,
        title=task.title,
        completed=task.completed,
        description=task.description
    )
    # Add the new task to our in-memory list
    tasks.append(new_task)
    # Increment the counter so the next task gets a different ID
    next_id += 1
    return new_task


def find_task_by_id(task_id: int) -> TaskResponse:
    """
    Find a task by its ID, or raise a 404 error if not found.

    This is a helper function (not an endpoint) used by other endpoints that need
    to look up a task by ID. It avoids duplicating the same search-and-error logic
    in multiple places.

    Args:
        task_id (int): The unique ID of the task to find.

    Returns:
        TaskResponse: The task with the matching ID.

    Raises:
        HTTPException: 404 error if no task with the given ID exists.
                       FastAPI automatically converts this into a JSON error response:
                       {"detail": "Task 5 not found"}
    """
    for task in tasks:
        if task.id == task_id:
            return task
    # HTTPException is FastAPI's way of returning error responses.
    # It stops the function and sends an HTTP error back to the client.
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


# {task_id} is a "path parameter" — it captures a value from the URL.
# For example, GET /tasks/3 sets task_id=3.
# FastAPI automatically converts it to an int (because of the type hint "task_id: int")
# and returns a 422 error if the value isn't a valid integer.
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    """
    Get a single task by its ID.

    Args:
        task_id (int): The unique ID of the task (from the URL path).

    Returns:
        TaskResponse: The task with the matching ID.

    Raises:
        HTTPException: 404 error if the task doesn't exist.

    Example:
        GET /tasks/1 → {"id": 1, "title": "Buy milk", ...}
    """
    return find_task_by_id(task_id)


@router.get("/search/", response_model=list[TaskResponse])
def search_tasks(q: str = Query(..., description="Search by title or description")):
    """
    Search tasks by keyword in title or description.

    Performs a case-insensitive search across all tasks. Returns any task whose
    title or description contains the search query.

    Args:
        q (str): The search query string, passed as a URL query parameter.
                 The "..." (Ellipsis) in Query(...) means this parameter is REQUIRED —
                 the client must provide it. If they don't, FastAPI returns a 422 error.

    Returns:
        list[TaskResponse]: A list of tasks matching the search query.
                            Returns an empty list if no tasks match.

    Example:
        GET /tasks/search/?q=milk
        → [{"id": 1, "title": "Buy milk", "description": "2% milk", ...}]
    """
    # Convert the query to lowercase so the search is case-insensitive.
    # "Buy Milk" will match "milk", "MILK", "Milk", etc.
    query = q.lower()

    # List comprehension — a compact way to filter a list in Python.
    # It reads like: "give me every task WHERE the query appears in the title OR description"
    results = [
        task for task in tasks
        if query in task.title.lower()
        or (task.description and query in task.description.lower())
    ]

    return results


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, updated_task: TaskUpdate):
    """
    Update an existing task with partial data.

    Only the fields you include in the request body will be changed.
    Omitted fields keep their current values. For example, sending just
    {"completed": true} will mark the task as done without changing the title
    or description.

    Args:
        task_id (int): The ID of the task to update (from the URL path).
        updated_task (TaskUpdate): The fields to update (from the request body).
                                   All fields are optional.

    Returns:
        TaskResponse: The updated task with all fields (changed and unchanged).

    Raises:
        HTTPException: 404 error if the task doesn't exist.

    Example:
        PUT /tasks/1 with body {"completed": true}
        → {"id": 1, "title": "Buy milk", "description": "2% milk", "completed": true}
    """
    # enumerate() gives us both the index (position in the list) and the task itself.
    # We need the index to replace the task at that exact position in the list.
    for index, existing_task in enumerate(tasks):
        if existing_task.id == task_id:
            # model_dump(exclude_unset=True) returns only the fields the client actually sent.
            # If they sent {"completed": true}, this gives us {"completed": True}.
            # Fields they didn't include are excluded, so we know not to overwrite them.
            update_data = updated_task.model_dump(exclude_unset=True)

            # Create a new TaskResponse starting from the existing task's data,
            # then overwrite only the fields the client provided.
            updated = TaskResponse(
                id=task_id,
                title=update_data.get("title", existing_task.title),
                description=update_data.get("description", existing_task.description),
                completed=update_data.get("completed", existing_task.completed),
            )
            # Replace the old task in the list with the updated one
            tasks[index] = updated
            return updated

    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@router.delete("/{task_id}", status_code=200)
def delete_task(task_id: int):
    """
    Delete a task by its ID.

    Removes the task from the in-memory list and returns a confirmation message
    along with the deleted task's data (so the client can see what was removed).

    Args:
        task_id (int): The ID of the task to delete (from the URL path).

    Returns:
        dict: A confirmation message and the deleted task's data.
              Example: {"message": "Task 1 deleted successfully", "task": {...}}

    Raises:
        HTTPException: 404 error if the task doesn't exist.
    """
    for index, task in enumerate(tasks):
        if task.id == task_id:
            # list.pop(index) removes the item at that position AND returns it.
            # This lets us both remove it from storage and send it back to the client
            # in a single operation.
            deleted_task = tasks.pop(index)
            return {"message": f"Task {task_id} deleted successfully", "task": deleted_task}

    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")