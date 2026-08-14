# Decisions

Short log of technical choices and why. Newest at the bottom.

## 2026-08-13 — Monorepo instead of separate repos

One repo with `backend/` and `frontend/` keeps the project easy to
clone, review, and CI in one place. Separate repos add overhead with
no benefit at this scale.

## 2026-08-13 — uv instead of pip/venv

uv handles the virtualenv, dependency resolution, and lockfile in one
tool, and it's fast. The `uv.lock` file makes CI and Docker builds
reproducible — everyone installs exactly the same versions.

## 2026-08-13 — FastAPI over Flask/Django

FastAPI gives automatic request validation via type hints and free
interactive API docs (/docs). Django is more than this project needs;
the data-heavy parts will live in separate pipeline scripts anyway.

## 2026-08-13 — Frontend runs outside Docker in development

The Next.js dev server (hot reload) is much faster running natively
than in a container on Windows. In production, Vercel builds the
frontend itself, so a frontend Dockerfile would go unused anyway.
Docker Compose only manages the backend and Postgres.

## 2026-08-13 — Postgres from day one (not SQLite)

Stage 2+ depends on Postgres-specific features (full-text search,
window functions for percentiles, eventually pgvector). Starting on
SQLite would mean migrating later for no gain.

## 2026-08-13 — CI green before tests exist

The pipeline runs lint + typecheck now and tolerates "no tests
collected" from pytest. This means the CI habit starts on commit one;
the pytest escape hatch gets removed in Stage 3 when real tests land.