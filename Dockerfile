FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /uvx /bin/

WORKDIR /project/
COPY pyproject.toml uv.lock /opt/

RUN uv sync -n --directory /opt/

COPY . /project/
ENV PATH="/opt/.venv/bin:$PATH"

RUN chmod +x /project/scripts/entrypoint.bot.sh
