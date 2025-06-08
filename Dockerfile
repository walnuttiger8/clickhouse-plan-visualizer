# Took this from https://github.com/astral-sh/uv-docker-example/blob/main/standalone.Dockerfile

FROM ghcr.io/astral-sh/uv:bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

ENV UV_PYTHON_INSTALL_DIR=/python
ENV UV_PYTHON_PREFERENCE=only-managed

RUN uv python install 3.13

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

FROM debian:bookworm-slim

COPY --from=builder --chown=python:python /python /python

COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH"

CMD ["fastapi", "run", "--host", "0.0.0.0", "/app/src/main.py"]