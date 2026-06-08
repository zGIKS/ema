from __future__ import annotations

import asyncio
import importlib.util
import os
import sys
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorClient


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_env() -> None:
    env_file = ROOT / ".env"
    if not env_file.exists():
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def _migration_files() -> list[Path]:
    return sorted(
        path
        for path in (ROOT / "mongo" / "migrations").glob("[0-9][0-9][0-9]_*.py")
        if path.name != "runner.py"
    )


async def _ensure_tracking_collection(db) -> None:
    await db.schema_migrations.create_index("name", unique=True)


async def _applied_migrations(db) -> set[str]:
    docs = await db.schema_migrations.find({}, {"name": 1}).to_list(length=None)
    return {doc["name"] for doc in docs}


async def _run_migration(db, migration_path: Path) -> None:
    spec = importlib.util.spec_from_file_location(migration_path.stem, migration_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load migration {migration_path.name}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[migration_path.stem] = module
    spec.loader.exec_module(module)

    await module.upgrade(db)
    await db.schema_migrations.insert_one({"name": migration_path.name})


async def main() -> None:
    await run_migrations()


async def run_migrations() -> None:
    _load_env()
    db_url = os.environ.get("FR_DB_URL")
    db_name = os.environ.get("FR_DB_NAME")
    if not db_url or not db_name:
        raise RuntimeError("FR_DB_URL and FR_DB_NAME are required")

    client = AsyncIOMotorClient(db_url)
    db = client[db_name]

    await _ensure_tracking_collection(db)
    applied = await _applied_migrations(db)

    for migration_path in _migration_files():
        if migration_path.name in applied:
            continue
        print(f"Applying {migration_path.name}")
        await _run_migration(db, migration_path)

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
