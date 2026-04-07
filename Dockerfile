# =============================================================================
# Dockerfile for Task Assistant API
# =============================================================================
#
# This file tells Docker how to build a container image for our FastAPI app.
# Think of it as a recipe — each instruction adds a "layer" to the image.
#
# What each section does:
#   1. FROM    — Start with a base image that already has Python installed
#   2. COPY uv — Install the uv package manager inside the container
#   3. WORKDIR — Set the folder where our app will live inside the container
#   4. COPY (dependency files first) — Copy pyproject.toml + uv.lock and install
#                                       (done FIRST for layer caching — see below)
#   5. COPY (app code) — Copy the rest of the project files into the container
#   6. EXPOSE  — Document which port the app listens on
#   7. CMD     — The command that runs when the container starts
# =============================================================================

# --- Step 1: Base Image ---
# We use python:3.11-slim instead of the full python:3.11 image.
# The "slim" variant is much smaller (~150MB vs ~900MB) because it only
# includes the minimum packages needed to run Python. This means faster
# downloads, faster builds, and less disk space used.
FROM python:3.11-slim

# --- Step 2: Install uv ---
# Copy the uv binary directly from its official Docker image.
# This is the recommended way to get uv inside a container — it's a single
# static binary, so no installation step is needed. Much faster than
# "pip install uv" or "curl | sh".
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# --- Step 3: Working Directory ---
# This creates the /app folder inside the container and makes it the
# default directory for all following commands. It's like running
# "mkdir /app && cd /app" in a terminal.
WORKDIR /app

# --- Step 4: Install Dependencies (with layer caching) ---
# WHY do we copy pyproject.toml and uv.lock BEFORE copying the rest of the code?
#
# Docker builds images in layers, and it caches each layer. If a layer
# hasn't changed, Docker reuses the cached version instead of rebuilding it.
#
# Dependencies change rarely, but your code changes constantly. By copying
# and installing dependencies FIRST, Docker can cache this expensive step.
# When you change your code but NOT your dependencies, Docker skips the
# "uv sync" step entirely — making rebuilds much faster (seconds vs minutes).
#
# If we copied everything at once, ANY code change would invalidate the cache
# and force a full reinstall of all dependencies every time.
COPY pyproject.toml uv.lock ./

# Install dependencies from the lockfile.
# --frozen: Don't update the lockfile, just install exactly what's in it.
#   This ensures the container gets the exact same versions you tested locally.
# --no-install-project: Only install dependencies, not the project itself.
#   We haven't copied the project code yet, so there's nothing to install —
#   this is just for the caching layer.
# --no-dev: Skip development-only dependencies (if any are added later).
RUN uv sync --frozen --no-install-project --no-dev

# --- Step 5: Copy Application Code ---
# Now copy the rest of the project files (main.py, app/ folder, etc.)
# into the container. This layer will be rebuilt whenever your code changes,
# but the dependency layer above stays cached.
COPY . .

# Sync again to install the project itself (now that the code is copied).
# This is fast because all dependencies are already cached from the step above.
RUN uv sync --frozen --no-dev

# --- Step 6: Expose Port ---
# This documents that the app listens on port 8000. It doesn't actually
# open the port — that happens when you run the container with "-p 8000:8000".
# Think of this as a note for anyone reading the Dockerfile.
EXPOSE 8000

# --- Step 7: Start Command ---
# "uv run" executes a command using the project's virtual environment.
# It automatically finds and uses the .venv that uv created during "uv sync".
# --host 0.0.0.0 = listen on all network interfaces (required inside Docker,
#   otherwise the app would only be accessible from inside the container itself)
# --port 8000 = listen on port 8000
# Note: we do NOT use --reload in production — it's a development-only feature
#   that watches for file changes. In a container, files don't change.
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
