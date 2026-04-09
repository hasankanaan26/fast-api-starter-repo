"""
Assignee router — defines all API endpoints for managing assignees.

Assignees are the people tasks can be assigned to. This router mirrors the
structure of tasks.py: a simple in-memory store with CRUD endpoints and a
keyword search. Tasks reference assignees by ID (see Task.assignee_id).

Endpoints defined here:
    GET    /assignees               — List all assignees
    POST   /assignees               — Create a new assignee
    GET    /assignees/{assignee_id} — Get a specific assignee by ID
    GET    /assignees/search/       — Search assignees by name or email
    PUT    /assignees/{assignee_id} — Update an assignee
    DELETE /assignees/{assignee_id} — Delete an assignee
"""

from fastapi import APIRouter, HTTPException, Query
from app.models import Assignee, AssigneeUpdate, AssigneeResponse

router = APIRouter(prefix="/assignees", tags=["assignees"])

# In-memory storage — same pattern as tasks.py. Resets on server restart.
assignees: list[AssigneeResponse] = []

# Monotonic counter for ID assignment. Lives at module scope so create_assignee
# can increment it across requests.
next_id = 1


def find_assignee_by_id(assignee_id: int) -> AssigneeResponse:
    """
    Find an assignee by ID, or raise 404 if not found.

    Helper used by the get/update/delete endpoints and (via exists_assignee_id)
    by the tasks router when validating task.assignee_id.
    """
    for assignee in assignees:
        if assignee.id == assignee_id:
            return assignee
    raise HTTPException(status_code=404, detail=f"Assignee {assignee_id} not found")


def exists_assignee_id(assignee_id: int) -> bool:
    """
    Non-raising existence check used by the tasks router.

    We keep this separate from find_assignee_by_id so the tasks router can
    produce its own error message ("Assignee X does not exist") without
    catching an HTTPException.
    """
    return any(a.id == assignee_id for a in assignees)


@router.get("", response_model=list[AssigneeResponse])
def list_assignees():
    """List all assignees currently stored."""
    return assignees


@router.post("", response_model=AssigneeResponse, status_code=201)
def create_assignee(assignee: Assignee):
    """
    Create a new assignee.

    Returns the stored assignee with its server-assigned ID.
    """
    global next_id

    new_assignee = AssigneeResponse(
        id=next_id,
        name=assignee.name,
        email=assignee.email,
    )
    assignees.append(new_assignee)
    next_id += 1
    return new_assignee


@router.get("/{assignee_id}", response_model=AssigneeResponse)
def get_assignee(assignee_id: int):
    """Get a single assignee by ID. Returns 404 if not found."""
    return find_assignee_by_id(assignee_id)


@router.get("/search/", response_model=list[AssigneeResponse])
def search_assignees(q: str = Query(..., description="Search by name or email")):
    """
    Case-insensitive search over name and email.

    Mirrors /tasks/search/ so the two endpoints feel consistent.
    """
    query = q.lower()
    return [
        a for a in assignees
        if query in a.name.lower() or query in a.email.lower()
    ]


@router.put("/{assignee_id}", response_model=AssigneeResponse)
def update_assignee(assignee_id: int, updated: AssigneeUpdate):
    """
    Partial update — only fields present in the request body are changed.
    """
    for index, existing in enumerate(assignees):
        if existing.id == assignee_id:
            update_data = updated.model_dump(exclude_unset=True)
            new_assignee = AssigneeResponse(
                id=assignee_id,
                name=update_data.get("name", existing.name),
                email=update_data.get("email", existing.email),
            )
            assignees[index] = new_assignee
            return new_assignee

    raise HTTPException(status_code=404, detail=f"Assignee {assignee_id} not found")


@router.delete("/{assignee_id}", status_code=200)
def delete_assignee(assignee_id: int):
    """
    Delete an assignee. Any tasks referencing this assignee are unassigned
    (their assignee_id is set back to None) so we don't leave dangling refs.
    """
    # Local import avoids a circular import at module load time:
    # tasks.py doesn't import this module, but we import its storage here.
    from app.routers import tasks as tasks_module

    for index, assignee in enumerate(assignees):
        if assignee.id == assignee_id:
            deleted = assignees.pop(index)

            # Unassign this person from every task that referenced them.
            # We rebuild each affected TaskResponse because the models are
            # immutable-ish (pydantic BaseModel allows mutation, but going
            # through the constructor keeps validation in the loop).
            for i, t in enumerate(tasks_module.tasks):
                if t.assignee_id == assignee_id:
                    tasks_module.tasks[i] = t.model_copy(update={"assignee_id": None})

            return {"message": f"Assignee {assignee_id} deleted successfully", "assignee": deleted}

    raise HTTPException(status_code=404, detail=f"Assignee {assignee_id} not found")
