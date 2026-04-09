"""
Data models for the Task Assistant API.

This file defines the "shape" of the data that flows through the API using Pydantic models.
Think of these models as blueprints — they describe what a Task looks like, what fields it has,
and what types those fields should be.

Pydantic is a data validation library that works hand-in-hand with FastAPI. When someone
sends a request to create a task, Pydantic automatically:
    1. Checks that all required fields are present
    2. Validates that each field is the correct type (e.g., "title" must be a string)
    3. Strips whitespace and enforces length constraints
    4. Returns a clear error message if anything is wrong

Why three models?
    - Task: Used for INPUT when CREATING — requires a title, description is optional.
    - TaskUpdate: Used for INPUT when UPDATING — all fields are optional so you can
                  send only what changed (e.g., just {"completed": true}).
    - TaskResponse: Used for OUTPUT — what the server sends back, including the ID.

Usage:
    # Creating a Task from incoming request data:
    task = Task(title="Buy groceries", description="Milk, eggs, bread")

    # Partial update — only change the completed status:
    update = TaskUpdate(completed=True)

    # Creating a TaskResponse to send back to the client:
    response = TaskResponse(id=1, title="Buy groceries", description="Milk, eggs, bread")
"""

from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

# Annotated types let us define reusable validation rules for strings.
# StringConstraints is the Pydantic v2 way to apply string-specific validation
# like stripping whitespace and enforcing length limits.
# We define these once here and reuse them across models — DRY (Don't Repeat Yourself).

# A task title: required, 1–100 chars, leading/trailing whitespace removed automatically.
# "strip_whitespace=True" means "  Buy milk  " becomes "Buy milk" before validation.
# "min_length=1" runs AFTER stripping, so "   " (all spaces) is correctly rejected.
TitleStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
]

# A task description: max 500 chars, whitespace stripped. No min_length because
# descriptions are optional — an empty string is fine.
DescriptionStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True, max_length=500),
]

# An assignee name: required, 1–100 chars, whitespace stripped.
# Same rules as TitleStr — a person's name shouldn't be blank or absurdly long.
NameStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
]

# An email address: 3–254 chars (RFC 5321 limit), whitespace stripped.
# We use a plain constrained string rather than EmailStr to avoid an extra
# dependency (email-validator). The length bounds catch the most obvious bad input.
EmailStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=3, max_length=254),
]


class Task(BaseModel):
    """
    Input model for creating a task.

    This model defines the data a client must send when creating a task.
    The "id" field is NOT included here because the server assigns IDs automatically —
    the client shouldn't be able to choose their own ID.

    Validation rules:
        - title: Required, 1–100 characters, whitespace is stripped automatically.
                 Blank/whitespace-only titles are rejected.
        - description: Optional (defaults to empty string), max 500 characters, stripped.
        - completed: Optional, defaults to False.

    Attributes:
        title (str): The name of the task (e.g., "Buy groceries"). Required.
        description (str): Additional details about the task. Optional, defaults to "".
        completed (bool): Whether the task is done. Defaults to False if not provided.

    Example:
        >>> task = Task(title="Study Python", description="Chapter 5", completed=False)
        >>> task.title
        'Study Python'
    """

    # Field() adds metadata (like the description) that shows up in the auto-generated
    # API docs at /docs. The actual validation (length, whitespace) comes from the
    # TitleStr/DescriptionStr types defined above.
    title: TitleStr = Field(
        ...,
        description="The name of the task",
    )
    # Description is optional — not every task needs extra details.
    # Defaults to an empty string so we never have to worry about None values.
    description: DescriptionStr = Field(
        default="",
        description="Additional details about the task",
    )
    # "default=False" makes this field optional.
    # If the client doesn't include "completed" in their request, it defaults to False.
    completed: bool = Field(
        default=False,
        description="Whether the task has been completed",
    )
    # Optional link to an assignee. None means "unassigned".
    # The router validates that this ID actually exists before saving the task.
    assignee_id: int | None = Field(
        default=None,
        description="ID of the assignee responsible for this task (None = unassigned)",
    )

    # model_config provides an example that shows up in the Swagger UI docs,
    # making it easier for users to understand the expected request format.
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Buy groceries",
                    "description": "Milk, eggs, and bread from the store",
                    "completed": False,
                    "assignee_id": 1,
                }
            ]
        }
    }


class TaskUpdate(BaseModel):
    """
    Input model for updating an existing task.

    Unlike Task, ALL fields here are optional. This lets clients send partial updates —
    for example, just {"completed": true} to mark a task as done without resending
    the title and description.

    Fields set to None are ignored during the update (the original value is kept).

    Attributes:
        title (str | None): New title, or None to keep the current title.
        description (str | None): New description, or None to keep the current one.
        completed (bool | None): New completed status, or None to keep the current one.

    Example:
        >>> update = TaskUpdate(completed=True)  # Only update the status
        >>> update.title is None  # Title stays unchanged
        True
    """

    # "TitleStr | None" means the value can be a valid title string OR None.
    # None means "don't change this field" — the router checks for None and
    # skips updating that field.
    title: TitleStr | None = Field(
        default=None,
        description="New title for the task (omit to keep current)",
    )
    description: DescriptionStr | None = Field(
        default=None,
        description="New description for the task (omit to keep current)",
    )
    completed: bool | None = Field(
        default=None,
        description="New completed status (omit to keep current)",
    )
    # Note: we can't distinguish "omit" from "explicitly set to None" using a plain
    # Optional field. The router uses model_dump(exclude_unset=True) to detect whether
    # the client actually sent this field, so passing assignee_id=null DOES unassign.
    assignee_id: int | None = Field(
        default=None,
        description="New assignee ID (omit to keep current, send null to unassign)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Buy oat milk instead",
                    "completed": True,
                    "assignee_id": 2,
                }
            ]
        }
    }


class Assignee(BaseModel):
    """
    Input model for creating an assignee.

    An assignee is a person who can be attached to one or more tasks. Like Task,
    this model is used for incoming request data — the server assigns the ID.

    Validation rules:
        - name: Required, 1–100 characters, whitespace stripped.
        - email: Required, 3–254 characters, whitespace stripped. Not a full
                 RFC-compliant email check, but catches the obviously bad cases.

    Attributes:
        name (str): The assignee's full name (e.g., "Jane Doe"). Required.
        email (str): The assignee's email address. Required.

    Example:
        >>> assignee = Assignee(name="Jane Doe", email="jane@example.com")
        >>> assignee.name
        'Jane Doe'
    """

    name: NameStr = Field(
        ...,
        description="The assignee's full name",
    )
    email: EmailStr = Field(
        ...,
        description="The assignee's email address",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Jane Doe",
                    "email": "jane@example.com",
                }
            ]
        }
    }


class AssigneeUpdate(BaseModel):
    """
    Input model for updating an existing assignee.

    Mirrors TaskUpdate: every field is optional so clients can send partial
    updates (e.g. just {"email": "new@example.com"}).

    Attributes:
        name (str | None): New name, or None to keep the current name.
        email (str | None): New email, or None to keep the current email.
    """

    name: NameStr | None = Field(
        default=None,
        description="New name for the assignee (omit to keep current)",
    )
    email: EmailStr | None = Field(
        default=None,
        description="New email for the assignee (omit to keep current)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "jane.doe@example.com",
                }
            ]
        }
    }


class AssigneeResponse(Assignee):
    """
    Output model for sending an assignee back to the client.

    Extends Assignee by adding the server-assigned "id" field.

    Attributes:
        id (int): The unique identifier assigned by the server. Starts at 1.
        name (str): Inherited from Assignee.
        email (str): Inherited from Assignee.
    """

    id: int = Field(..., description="Unique assignee identifier assigned by the server")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": "Jane Doe",
                    "email": "jane@example.com",
                }
            ]
        }
    }


class TaskResponse(Task):
    """
    Output model for sending a task back to the client.

    This model extends Task by adding an "id" field. It's used in API responses
    so the client can see the server-assigned ID for each task.

    The "(Task)" in the class definition means TaskResponse *inherits* from Task —
    it gets all of Task's fields (title, description, completed) automatically,
    plus the new "id" field defined here.

    Attributes:
        id (int): The unique identifier assigned by the server. Starts at 1.
        title (str): Inherited from Task.
        description (str): Inherited from Task.
        completed (bool): Inherited from Task.

    Example:
        >>> response = TaskResponse(id=1, title="Study Python", description="Chapter 5")
        >>> response.id
        1
    """

    id: int = Field(..., description="Unique task identifier assigned by the server")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title": "Buy groceries",
                    "description": "Milk, eggs, and bread from the store",
                    "completed": False,
                    "assignee_id": 1,
                }
            ]
        }
    }
