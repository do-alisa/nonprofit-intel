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

## 2026-08-25 — URL as the source of truth for search state

The search query lives in `?q=` rather than component state. Back
navigation, refresh, and link-sharing all restore the search for
free, and TanStack Query serves cached results instantly on return.
Tradeoff learned along the way: every internal link that should
preserve state has to carry it explicitly (the "← Search" link
initially dropped it). Same pattern will apply to Stage 3's filter
UI — all filters belong in the URL.

## 2026-08-25 — router.replace over router.push for searches

Each new search replaces the URL instead of pushing a history
entry, so the back button always means "leave the page" instead of
stepping through old searches.

## 2026-08-25 — Dark mode removed from starter template

The create-next-app CSS auto-switches to dark based on OS settings,
but our components assume a light background (white-on-white hover
states, unreadable chart tooltips). Deleted the dark block; real
dark mode means auditing every color, which isn't worth it for a
prototype.

## 2026-08-25 — Gitignore templates don't compose in a monorepo

GitHub's Python .gitignore ignores `lib/`, which silently excluded
`frontend/src/lib/` — worked locally, failed in CI because the file
was never committed. Fixed with a `!frontend/src/lib/` negation in
the root .gitignore. Diagnostic that found it: `git check-ignore -v
<path>`. Second lesson: negation patterns are relative to the
.gitignore file they live in, so the fix had to go in the root file,
not `frontend/.gitignore`.

## 2026-08-25 — Config via environment variables, not code

CORS origins (`ALLOWED_ORIGINS`) and port (`PORT`) come from env
vars with local-dev defaults, so the same Docker image runs locally
and on Railway with no per-environment code changes. Also pinned the
container start command to `uv run --frozen --no-dev` — `uv run`
re-syncs dependencies at startup by default and was installing dev
tooling (ruff, pytest) into the production container.

## 2026-08-25 — Railway (backend) + Vercel (frontend)

Vercel is the natural Next.js host. Railway over Render's free tier
because free Render services sleep when idle and cold-start slowly —
bad during a live demo. Costs a few dollars/month after trial
credit; accepted for recruiting season. Deferred adding Railway's
Postgres until Stage 2 since Stage 1 doesn't touch the database.
