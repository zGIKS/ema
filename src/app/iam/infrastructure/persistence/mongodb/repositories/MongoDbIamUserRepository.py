from __future__ import annotations

from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.app.iam.domain.model.entities import IamUser
from src.app.iam.domain.model.valueobjects import UserId, UserRole
from src.app.iam.domain.repositories import IamUserRepository


class MongoDbIamUserRepository(IamUserRepository):
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self._collection = database.iam_users

    def _to_domain(self, doc: dict) -> IamUser:
        return IamUser(
            user_id=UserId(doc["user_id"]),
            username=doc["username"],
            password_hash=doc["password_hash"],
            role=UserRole.from_value(doc["role"]),
            is_active=bool(doc.get("is_active", True)),
        )

    async def find_by_username(self, username: str) -> IamUser | None:
        doc = await self._collection.find_one({"username": username})
        if doc is None:
            return None
        return self._to_domain(doc)

    async def find_by_id(self, user_id: UserId) -> IamUser | None:
        doc = await self._collection.find_one({"user_id": user_id.value})
        if doc is None:
            return None
        return self._to_domain(doc)

    async def save(self, user: IamUser) -> IamUser:
        now_epoch = int(datetime.now(UTC).timestamp())
        await self._collection.update_one(
            {"user_id": user.user_id.value},
            {
                "$set": {
                    "user_id": user.user_id.value,
                    "username": user.username,
                    "password_hash": user.password_hash,
                    "role": user.role.value,
                    "is_active": user.is_active,
                    "updated_at": now_epoch,
                },
                "$setOnInsert": {"created_at": now_epoch},
            },
            upsert=True,
        )
        return user
