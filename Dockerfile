# syntax=docker/dockerfile:1

# ---- builder: resolve and install dependencies from the lockfile ----
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12.15 /uv /uvx /bin/

WORKDIR /app

# Only the dependency manifests are needed to build the venv — pyproject.toml
# has [tool.uv] package = false, so uv never installs our own app/ as a
# package, meaning app code never has to be present for this layer at all.
# Copying just these two files means Docker's layer cache is reused on every
# rebuild where only app code changed, not dependencies.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev


# ---- runtime: minimal image, no uv/build tools, non-root ----
FROM python:3.12-slim AS runtime

RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY app ./app
COPY alembic.ini ./
COPY migrations ./migrations

ENV PATH="/app/.venv/bin:$PATH"

USER appuser
EXPOSE 8000

# Migrations are intentionally NOT run automatically here. In the
# multi-replica Kubernetes deployment planned for Stage 7, every pod
# auto-migrating on boot would race to apply the same migration
# concurrently. Migrations will instead run as a one-shot Kubernetes Init
# Container ahead of the app Deployment, reusing this same image with its
# command overridden to `alembic upgrade head` instead of the CMD below —
# that's also why alembic.ini and migrations/ are still copied into this
# image even though the normal CMD never touches them.
#
# For local testing: run migrations manually before starting this
# container, e.g. `uv run alembic upgrade head` against the target database.
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
