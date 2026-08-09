# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Telegram bot (Russian-language) for administering a boxing club group chat. Implements user
registration/lookup and a daily attendance poll; the README lists further planned features around
auto-generated training-session pools, cancellations, and attendance statistics that are not yet
implemented.

Stack: `aiogram` 3 (bot framework), `dishka` (async DI container), `SQLAlchemy` 2 async + `asyncpg` +
`alembic` (Postgres), `pydantic` / `pydantic-settings` (schemas & config), `loguru` (logging),
`apscheduler` (in-process cron for the attendance poll), `uv` (dependency management). There is no
message broker/task queue in this repo — `docker-compose.yml` has no `rabbitmq` service.

## Commands

Dependencies are managed with `uv`; there is no separate lockfile-install step beyond `uv sync`.

```bash
uv sync                                           # install deps (creates .venv)
uv run ruff check --fix app                       # lint (auto-fix) — CI/pre-commit scope is `app` only
uv run ruff format app                            # format
uv run mypy --config-file ./mypy.ini app           # type-check (strict mode)
pre-commit run --all-files                        # run all hooks (ruff, mypy, whitespace/AST checks, etc.)
```

There is no test suite in this repo (no `tests/` dir, no pytest config) — don't assume one exists.

Running the bot is Docker-only (via `go-task`, see `Taskfile.yml`):

```bash
task run    # alias: task r  — docker compose up --build -d (app + migrations + postgres)
task down   # alias: task d  — docker compose down --remove-orphans
task log    # alias: task l  — docker compose logs -f
task create-migration -- "message"   # alias: task cm — alembic revision --autogenerate inside the app container
```

`docker-compose.yml` services: `app` (the bot), `migrations` (runs `alembic upgrade head` once and exits,
gates `app` startup), `db` (postgres:17-alpine, exposed on host port `14141`).

Inside the container, `scripts/entrypoint.bot.sh` branches on `APP__DEV_MODE`: `true` runs `pymon
app/__main__.py` (auto-reload), otherwise `python -m app`.

Config is env-based via `.env` (see `.env-example`), all vars prefixed `APP__` (e.g. `APP__BOT_TOKEN`,
`APP__DB_HOST`) per `app/settings.py`'s `pydantic-settings` config (`env_prefix="APP__"`,
`env_nested_delimiter="__"`).

## Architecture

Layered/clean-architecture style, one feature vertical per domain concept (currently only `user`):

```
domain    -> plain pydantic entities + domain exceptions, no framework deps
repos     -> SQLAlchemy queries against ORM tables; convert DB rows <-> domain entities
services  -> business logic; orchestrate repo calls + commit via UoW
usecases  -> one class per action, thin `__call__` wrapper around a service method (what handlers call)
handlers / routers -> aiogram Routers; resolve deps (services/usecases/current user) via dishka injection
infra/db  -> SQLAlchemy declarative tables (`infra/db/tables/`) + alembic migrations
di        -> dishka Provider classes, one per concern, wired together in `di/containers.py`
```

Data flow for a request: aiogram `Router` handler (decorated `@inject`) → `usecases.*UseCase.__call__` →
`services.*Service` method → `repos.*Repo` → SQLAlchemy `AsyncSession`. Domain entities
(`app.domain.user.entities.User`, a pydantic `BaseModel`) are the shared currency between
service/usecase/handler layers; `repos/user/converters.py` maps `UserTable` (SQLAlchemy) rows to/from them.

**DI (dishka).** `app/di/containers.py:default_providers()` lists every `Provider` (settings, database,
repos, services, usecases, user-resolution, aiogram integration). Container is built once in
`app/entrypoint.py` and attached to the aiogram dispatcher via `setup_dishka(..., auto_inject=True)`, so
handlers get dependencies through `FromDishka[...]` annotations plus `@inject` without manual container
calls. `app/di/providers/user.py` is the important one to know: it resolves the current-request
`FromDishka[User]` by pulling `from_user.id`/`username` off the incoming `Message` and calling
`GetOrCreateTgUserUseCase` — i.e. **every message handler implicitly gets-or-creates a `User` row** for
the sender before the handler body runs.

**Scopes.** `AsyncSession` is `Scope.REQUEST` (one session per aiogram update) and is also provided as the
`UoW` protocol (`app/infra/uow.py`) via dishka's `AnyOf` — services depend on `UoW`, not on SQLAlchemy
directly, and call `.commit()` explicitly after a write (no auto-commit; `expire_on_commit=False`).
Engine/sessionmaker are `Scope.APP` singletons.

**Bot/dispatcher singletons.** `app/bot.py` holds `Bot`/`Dispatcher` as lazily-initialized module globals
(`get_bot()`/`get_dispatcher()`) — the classic pattern for code that needs to import the same
bot/dispatcher instance elsewhere (e.g. a scheduled job reaching for `bot.send_poll` outside a handler).
Routers live under `app/handlers/` (one subpackage per surface, e.g. `app/handlers/telegram/`) and are
registered on the dispatcher explicitly in `app/entrypoint.py:entrypoint()` — not auto-discovered.

**Scheduled jobs.** `entrypoint()` starts an `apscheduler` `AsyncIOScheduler` (timezone from
`settings.timezone`, default `Europe/Moscow`) and registers a cron job (`app/scheduler/factory.py`,
Mon/Wed/Fri at 10:00) that sends an attendance poll (`bot.send_poll`, via `app/scheduler/tasks.py`) to
`settings.target_chat`. This is the only scheduled/background work in the app — there is no task queue.

**Middleware.** Two dispatcher-wide `update` middlewares are registered in `entrypoint()`, in this order:
`ChatInfoMiddleware` (`app/middlewaries/aiogram/chat_info.py`) logs chat/user info for every update via
`loguru`, then `ErrorMiddleware` (`app/middlewaries/aiogram/error_handler.py`) wraps the rest of the
pipeline: on unhandled exception it replies to the user, opens its own dishka `Scope.REQUEST` container
(independent of the failed handler's) to fetch staff users and DM them a formatted traceback, then
re-raises. Note: `_notify_staff` calls `UserRepo.get_staff_users()`, which does not exist on `UserRepo`
(`app/repos/user/repo.py`) — this fails silently (caught, logged, no notification sent) until that method
is added.

**Logging.** stdlib `logging` is intercepted and routed through `loguru` (`app/logger.py`); call
`configure_logging()` once at startup (already done in `entrypoint()`). Prefer `loguru`'s `logger` in new
handler/service code, matching existing modules like `error_handler.py`.

**Migrations.** Alembic env (`app/infra/db/migrations/env.py`) targets `BaseTable.metadata` (imported from
`app/infra/db/__init__.py`, which re-exports every table module) — new SQLAlchemy tables must be added to
that `__init__.py`'s exports to be picked up by autogenerate. Revision filenames are timestamp-prefixed
(`alembic.ini` `file_template`).

## Notes on in-progress code

`app/handlers/` (renamed from a prior `app/routers/`) and `app/middlewaries/` are the working, wired-in
implementations — not scaffolding. The one known gap is `UserRepo.get_staff_users()`, referenced by
`ErrorMiddleware` but not implemented (see above); before assuming any other repo/service method exists,
check `app/repos/user/repo.py` and `app/services/user/service.py` directly rather than trusting call sites.
