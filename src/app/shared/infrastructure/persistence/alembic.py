from __future__ import annotations

import asyncio
from pathlib import Path

from alembic import command
from alembic.config import Config

from src.app.shared.config import settings


def _build_alembic_config() -> Config:
    # Alembic is driven in-process so startup can apply migrations automatically.
    project_root = Path(__file__).resolve().parents[5]
    config = Config()
    config.set_main_option("script_location", str(project_root / "migrations"))
    config.set_main_option("sqlalchemy.url", settings.db_url)
    return config


def upgrade_database() -> None:
    command.upgrade(_build_alembic_config(), "head")


async def upgrade_database_async() -> None:
    await asyncio.to_thread(upgrade_database)
