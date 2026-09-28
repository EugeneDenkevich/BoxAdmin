# Repository Guidelines

## Project Structure

The Python application lives in `app/`. Keep business entities and exceptions in `domain/`, orchestration in `usecases/`, application logic in `services/`, and persistence behind `repos/` and `infra/`. Telegram handlers and middleware are under `handlers/` and `middlewaries/`; dependency injection is in `di/`, and scheduled jobs are in `scheduler/`. Database tables and Alembic migrations live in `infra/db/`. `scripts/` contains the container entrypoint; project, lint, type-check, and Compose settings are configured at the repository root.

## Build, Test, and Development

Python 3.13 or newer and `uv` are required. Install application and development dependencies with `uv sync --group dev`. Copy `.env-example` to `.env` and set the Telegram token and target chat before starting the services.

- `docker compose up --build -d` builds and starts the bot, migrations, and PostgreSQL.
- `docker compose logs -f` follows service logs; `docker compose down --remove-orphans` stops the stack.
- `uv run ruff check app` checks Python lint rules.
- `uv run mypy --config-file mypy.ini app` runs strict type checking.

## Coding Style

Use four spaces, double-quoted strings, and an 88-character line limit. Follow Ruff’s configured import ordering and lint rules. Use `snake_case` for modules, functions, and variables, and `PascalCase` for classes. Keep changes within the existing application layers and add schema changes as Alembic migrations under `app/infra/db/migrations/versions/`.

## Testing

There is no test suite in the repository yet. For Python changes, run Ruff and mypy; for behavior that depends on Telegram or PostgreSQL, verify it with the relevant Compose services and review their logs.

## Commits and Pull Requests

Recent commits use short type prefixes such as `feat:` and `chore:`; follow that pattern with a concise description (for example, `feat: add pool cancellation`). Pull requests should explain the user-visible change, note configuration or migration impacts, and list checks performed. Link a related issue when one exists.

## Configuration and Secrets

Keep local credentials in `.env`, which is ignored by Git. Use `.env-example` to document required settings without committing real tokens or passwords.
