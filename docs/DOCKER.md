# Docker Guide

This guide explains the project's `Dockerfile` line by line, the supporting `.dockerignore`, and the `docker build` / `docker run` commands you'll use day-to-day — including every flag that's worth knowing.

If you're new to Docker: a **Dockerfile** is a recipe, an **image** is the compiled result of that recipe, and a **container** is a running instance of an image. You build an image once, then run as many containers from it as you like.

---

## The Dockerfile

Here is the full file, followed by an explanation of each instruction.

```dockerfile
FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY . .
RUN uv sync --frozen --no-dev

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `FROM python:3.11-slim`

Every image starts from a **base image**. We use `python:3.11-slim`, an official Python image built on a stripped-down Debian. The `slim` variant is ~150 MB instead of the full image's ~900 MB because it only includes what's needed to run Python — no compilers, no docs, no extra system tools. Smaller images mean faster downloads, faster builds, and a smaller attack surface.

### `COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/`

This is a **multi-stage copy**: it pulls the `uv` binary directly out of its official image and drops it into `/bin/` in our image. `uv` is a single static binary, so there's nothing to "install" — we just copy the file. This is much faster and more reliable than `pip install uv` or downloading it with `curl`.

### `WORKDIR /app`

Creates `/app` inside the container and makes it the working directory for every subsequent instruction. It's the equivalent of running `mkdir /app && cd /app`. All relative paths in later `COPY` and `RUN` commands are resolved against `/app`.

### `ENV UV_LINK_MODE=copy` and `UV_COMPILE_BYTECODE=1`

Two environment variables that tune `uv` for containers:

- **`UV_LINK_MODE=copy`** — by default `uv` tries to hardlink files from its cache into the virtualenv. Inside Docker, the cache and the target are often on different filesystems, which produces noisy warnings and a fallback. Setting this to `copy` just silences the dance and copies the files directly.
- **`UV_COMPILE_BYTECODE=1`** — pre-compiles Python source files to `.pyc` bytecode at install time. This makes the container's first request a bit faster because Python doesn't have to compile modules on import.

### `COPY pyproject.toml uv.lock ./` then `RUN uv sync --frozen --no-install-project --no-dev`

This is the **layer-caching trick** and it's the single most important thing in the file. Docker builds images in layers and caches each one. If the inputs to a layer haven't changed, Docker reuses the cached layer instead of rebuilding it.

Dependencies change rarely; your code changes constantly. By copying **only** the dependency files first and installing from them, the "install dependencies" layer is cached until `pyproject.toml` or `uv.lock` actually changes. When you edit `main.py`, Docker reuses the cached dependency layer and your rebuild takes seconds instead of minutes.

The flags on `uv sync`:

- **`--frozen`** — don't update `uv.lock`, install exactly what's pinned there. This guarantees the container gets the same versions you tested locally.
- **`--no-install-project`** — install dependencies but **not** the project itself. We haven't copied the project code yet, so there'd be nothing to install. This is the "dependencies-only" cache layer.
- **`--no-dev`** — skip development-only dependencies (testing tools, linters, etc.). Keeps the image lean.

### `COPY . .` then `RUN uv sync --frozen --no-dev`

Now we copy the rest of the project into `/app`. Any code change invalidates this layer — but the expensive dependency layer above is still cached, so this step is fast.

The second `uv sync` installs the **project itself** (what `--no-install-project` skipped before). All its dependencies are already present, so this is near-instant.

### `EXPOSE 8000`

Documents that the container listens on port 8000. **This does not actually open a port** — it's metadata. Publishing the port to your host happens at `docker run` time with `-p`.

### `CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]`

The default command that runs when a container starts from this image.

- **`uv run`** — runs a command inside the project's virtualenv (the `.venv` that `uv sync` created). You don't need to activate anything.
- **`uvicorn main:app`** — starts the Uvicorn ASGI server, loading the `app` object from `main.py`.
- **`--host 0.0.0.0`** — listen on all network interfaces. This is **required** inside Docker. If you used the default `127.0.0.1`, the server would only accept connections from inside the container, and `docker run -p` would appear to do nothing.
- **`--port 8000`** — listen on port 8000. Must match the port in `EXPOSE` and the container side of your `-p` mapping.
- **No `--reload`** — reload mode is for development only. In a container, files don't change at runtime.

`CMD` uses the **exec form** (a JSON array) rather than shell form (a plain string). Exec form runs the command as PID 1 directly, which means signals like `Ctrl+C` and `docker stop` reach your app cleanly.

---

## The `.dockerignore` File

```
.venv
__pycache__
**/__pycache__
*.py[oc]
.git
.gitignore
.env
docs
README.md
Dockerfile
.dockerignore
```

`.dockerignore` works like `.gitignore`, but for Docker. Before building, Docker packages up everything in the build directory and sends it to the Docker daemon as the **build context**. Anything not excluded gets shipped over and potentially baked into the image.

Without this file, Docker would upload your local `.venv` (hundreds of megabytes), `.git` history, `__pycache__` folders, and docs on every single build. That's slow, bloats the image, and risks baking secrets like `.env` into a layer where they'd be hard to remove.

Rule of thumb: ignore anything that isn't needed **at runtime inside the container**.

---

## Building the Image

```bash
docker build -t task-assistant .
```

That's the command you'll actually use. Here's what each piece does, plus the flags worth knowing:

- **`docker build`** — the command that reads a Dockerfile and produces an image.
- **`-t task-assistant`** — **tag** the resulting image with the name `task-assistant`. Without a tag, the image only has a random hash ID and you'd have to reference it by that hash. You can also version tags: `-t task-assistant:1.0`, `-t task-assistant:dev`. The default tag is `latest`.
- **`.`** — the **build context**: the directory Docker sends to the daemon. The `.` means "the current directory". The Dockerfile must be inside this directory (or pointed to with `-f`).

Other flags you may reach for:

- **`-f path/to/Dockerfile`** — use a Dockerfile at a non-default path. Handy if you have `Dockerfile.dev` and `Dockerfile.prod`.
- **`--no-cache`** — ignore the layer cache and rebuild everything from scratch. Use this when you suspect a cached layer is wrong, or when you want to pick up fresh security updates from the base image.
- **`--pull`** — always pull the latest version of the base image (`python:3.11-slim`) instead of using the locally cached copy.
- **`--build-arg KEY=value`** — pass a value into a Dockerfile `ARG`. This Dockerfile doesn't use any, but it's how you'd parameterize things like the Python version.
- **`--progress=plain`** — show full, non-collapsed build output. Useful for debugging why a layer is failing.
- **`--platform linux/amd64`** — build for a specific CPU architecture. Relevant on Apple Silicon Macs when the target server is x86.

---

## Running the Container

```bash
docker run -p 8000:8000 --env-file .env task-assistant
```

Then open http://localhost:8000.

Breakdown:

- **`docker run`** — creates a new container from an image and starts it.
- **`-p 8000:8000`** — **publish** a port. The format is `HOST:CONTAINER`. The left side is the port on your machine; the right side is the port inside the container (which must match what Uvicorn is listening on). `-p 9000:8000` would let you reach the app at `localhost:9000`.
- **`--env-file .env`** — read environment variables from a file and pass them into the container. Each line in the file should be `KEY=value`. Drop this flag if the app doesn't need any env vars.
- **`task-assistant`** — the image to run (the tag you built above). This must be the last positional argument before any override command.

Other flags worth knowing:

- **`-d`** / **`--detach`** — run in the background and print the container ID. Without this, your terminal is attached to the container and closing it stops the app. Pair with `docker logs` and `docker stop`.
- **`--rm`** — automatically remove the container when it exits. Great during development so you don't accumulate stopped containers. Don't use it in production if you want to inspect crashed containers.
- **`--name my-api`** — give the container a friendly name instead of the auto-generated one (like `dreamy_einstein`). Lets you do `docker stop my-api` instead of copying a hash.
- **`-e KEY=value`** — set a single environment variable inline. You can repeat the flag. Useful for one-off overrides on top of `--env-file`.
- **`-v /host/path:/container/path`** — mount a **volume**: expose a directory from your host inside the container. The main use case is persistent data (e.g., a database folder) or live-editing code during development.
- **`-it`** — short for `--interactive --tty`. Required if you want to run a shell inside the container: `docker run -it task-assistant bash`. Not needed for server processes.
- **`--restart unless-stopped`** — restart policy. If the container crashes (or the host reboots), Docker will start it back up unless you explicitly stopped it. Useful for long-running services.
- **`--network host`** — share the host's network stack instead of creating a bridge. Linux-only. Skips the need for `-p` but reduces isolation.

Putting several together, a realistic "run it and forget it" command:

```bash
docker run -d --rm --name task-assistant -p 8000:8000 --env-file .env task-assistant
```

---

## Managing Running Containers

Once the container is running (especially with `-d`), these commands become your toolkit:

- **`docker ps`** — list running containers. Add `-a` to include stopped ones.
- **`docker logs <name-or-id>`** — print the container's stdout/stderr. Add `-f` to follow new output like `tail -f`.
- **`docker stop <name-or-id>`** — gracefully stop a container (sends SIGTERM, then SIGKILL after 10 seconds).
- **`docker rm <name-or-id>`** — remove a stopped container. Add `-f` to force-remove a running one.
- **`docker exec -it <name-or-id> bash`** — open a shell **inside a running container**. Invaluable for poking around ("is the file actually there?", "what does the env look like?").
- **`docker images`** — list images on your machine.
- **`docker rmi <image>`** — remove an image. You must remove all containers using it first.
- **`docker system prune`** — clean up stopped containers, dangling images, and unused networks. Add `-a` to be more aggressive. Run it occasionally to reclaim disk space.

---

## Common Gotchas

- **"I can't reach the app at localhost:8000."** Check three things: (1) did you pass `-p 8000:8000`? (2) is Uvicorn bound to `0.0.0.0` and not `127.0.0.1`? (3) did the app actually start — run `docker logs` to see.
- **"My code changes aren't showing up."** Containers run the code that was baked into the image at build time. Rebuild (`docker build`) and run a new container. For a true hot-reload dev workflow, you'd mount the code as a volume (`-v "$(pwd):/app"`) and run Uvicorn with `--reload`.
- **"Every build reinstalls all dependencies."** Something is invalidating the dependency-layer cache. Check that `pyproject.toml` and `uv.lock` haven't changed, and that `.dockerignore` is excluding files that change on every build.
- **"The image is huge."** Make sure `.dockerignore` is excluding `.venv`, `.git`, `__pycache__`, and any large local-only folders. Check image size with `docker images`.
- **"`.env` isn't being picked up."** `--env-file` reads a file on the **host** at `docker run` time. The file must exist at the path you pass, relative to where you ran the command.
