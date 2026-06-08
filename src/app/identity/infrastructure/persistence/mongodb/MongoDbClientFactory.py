from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

class MongoDbClientFactory:
    def __init__(self, db_url: str, db_name: str) -> None:
        self._client = AsyncIOMotorClient(db_url)
        self._db_name = db_name

    def database(self) -> AsyncIOMotorDatabase:
        return self._client[self._db_name]

    async def init_database(self) -> None:
        db = self.database()
        await db.persons.create_index("person_id", unique=True)
        await db.persons.create_index("dni", unique=True)
        await db.usage_logs.create_index("used_at")
        await db.usage_logs.create_index("operation")
