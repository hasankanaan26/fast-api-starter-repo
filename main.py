"""
Main entry point for the Task Assistant API.

This file is the starting point of the entire application. It does three things:
    1. Creates a FastAPI application instance (the core object that handles all requests)
    2. Registers the task router (connects the /tasks endpoints to the app)
    3. Defines a health check endpoint (a simple way to verify the server is running)

FastAPI is a modern Python web framework that makes it easy to build APIs.
When you run "uvicorn main:app", uvicorn looks in this file for a variable called "app"
and uses it to start the web server.

Usage:
    Run the server with:
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
    Then visit http://localhost:8000/docs for interactive API documentation.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import tasks, chat, assignees


# Create the FastAPI application instance.
# This is the central object that coordinates everything:
#   - title, description, version: These show up in the auto-generated API docs at /docs
#   - FastAPI automatically generates interactive documentation (Swagger UI) from this info
app = FastAPI(
    title="Task Assistant API",
    description="API for Task Assistant",
    version="1.0.0",
)

# Enable CORS so the static HTML UI (served from a separate origin, e.g. a
# local file or a dev server on a different port) can call these endpoints
# from the browser. For a local-only dev tool we allow everything; tighten
# this list before deploying anywhere public.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the tasks router with the app.
# A "router" is a group of related endpoints. Instead of defining every route in this file,
# we organize them into separate files (routers). This keeps the code clean and modular.
# The tasks router adds all the /tasks/* endpoints (create, read, update, delete, search).
app.include_router(tasks.router)

# Register the assignees router — adds the /assignees/* endpoints for managing
# the people that tasks can be assigned to. Tasks reference assignees by ID
# via the Task.assignee_id field.
app.include_router(assignees.router)

# Register the chat router — adds POST /chat, which proxies messages to a local
# Ollama model using the OLLAMA_BASE_URL and OLLAMA_MODEL values from .env.
app.include_router(chat.router)


# The @app.get("/health") line is a "decorator" — it tells FastAPI:
# "When someone sends a GET request to /health, call the function below."
# Decorators modify the behavior of the function they sit above.
@app.get("/health")
def health_check():
    """
    Health check endpoint — verifies the server is running.

    This is a simple endpoint that returns a fixed response. It's commonly used by:
        - Developers: to quickly check if the server started correctly
        - Load balancers: to know if this server instance is healthy
        - Monitoring tools: to alert you if the server goes down
        - Docker: for container health checks

    Returns:
        dict: A JSON object with the server status.
              Example: {"status": "ok", "checkpoint": 1}
    """
    return {"status": "ok", "checkpoint": 1}
