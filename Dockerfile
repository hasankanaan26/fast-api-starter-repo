FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app

ARG UV_LINK_MODE=copy
ARG UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=${UV_LINK_MODE} \
    UV_COMPILE_BYTECODE=${UV_COMPILE_BYTECODE}

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY . .
RUN uv sync --frozen --no-dev

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
