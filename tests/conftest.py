import asyncio
import os
import subprocess
from collections.abc import Generator
from uuid import uuid4

import asyncpg
import pytest
from sqlalchemy import URL

from app.settings import Settings, get_settings


async def run_admin_sql(settings: Settings, sql: str) -> None:
    connection = await asyncpg.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_pass,
        database="postgres",
    )

    try:
        await connection.execute(sql)
    finally:
        await connection.close()


@pytest.fixture(scope="session")
def test_database_url() -> Generator[URL, None, None]:
    settings = get_settings()
    database_name = f"test_app_{uuid4().hex}"

    asyncio.run(run_admin_sql(settings, f'CREATE DATABASE "{database_name}"'))

    try:
        environment = os.environ.copy()
        environment["APP__DB_NAME"] = database_name

        subprocess.run(["alembic", "upgrade", "head"], env=environment, check=True)

        yield settings.get_db_url().set(database=database_name)
    finally:
        asyncio.run(
            run_admin_sql(
                settings,
                f'DROP DATABASE IF EXISTS "{database_name}" WITH (FORCE)',
            ),
        )
