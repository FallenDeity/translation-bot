import os
import typing as t

from motor import motor_asyncio

from .models import Log as LogModel
from .models import Novel
from .models import Warn as WarnModel

if t.TYPE_CHECKING:
    from src.core.logger import Logger


__all__: tuple[str, ...] = ("Database",)


class Database:
    def __init__(self, logger: "Logger") -> None:
        self._client: motor_asyncio.AsyncIOMotorClient = motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"))
        self._logger = logger
        self._db: motor_asyncio.AsyncIOMotorDatabase = self._client["database"]
        self.warns: Warn = Warn(self._db)
        self.library: Library = Library(self._db)
        self._logger.info("Connected to MongoDB!")


class Library:
    titles: list[str] | None = None
    tags: list[str] | None = None
    count: int = 0

    def __init__(self, pool: motor_asyncio.AsyncIOMotorCollection) -> None:
        self._pool = pool["library"]
        self.current_count = 0

    async def get_novel(self, novel_id: int) -> Novel | None:
        novel: dict[str, t.Any] | None = await self._pool.find_one({"id": novel_id}, {"_id": 0})
        return Novel.from_dict(novel) if novel else None

    async def get_novels(self, novel_ids: list[int]) -> list[Novel]:
        novels: list[dict[str, t.Any]] = await self._pool.find({"id": {"$in": novel_ids}}, {"_id": 0}).to_list(None)
        return [Novel.from_dict(novel) for novel in novels]

    async def get_user_novel_count(self, user_id: int | None = None, _top_200: bool = False) -> dict[int, int]:
        if user_id is None:
            top_200_uploaders = await self._pool.aggregate(
                [
                    {"$group": {"_id": "$uploader", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 200},
                ]
            ).to_list(None)
            return {top_200_uploader["_id"]: top_200_uploader["count"] for top_200_uploader in top_200_uploaders}
        count = await self._pool.count_documents({"uploader": user_id})
        user_rank = await self._pool.aggregate(
            [
                {"$group": {"_id": "$uploader", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gt": count}}},
                {"$count": "count"},
            ]
        ).to_list(None)
        return {user_id: user_rank[0]["count"] + 1 if user_rank else 1}

    async def add_novel(self, novel: Novel) -> None:
        if await self._pool.count_documents({"id": novel.id}):
            return await self.update(novel)
        await self._pool.insert_one(novel.to_dict())

    async def remove_novel(self, novel_id: int) -> None:
        await self._pool.delete_one({"id": novel_id})

    async def update_novel(self, novel_id: int, **kwargs: t.Any) -> None:
        kwargs = {key: value for key, value in kwargs.items() if value}
        await self._pool.update_one({"id": novel_id}, {"$set": kwargs})

    async def get_all_novels(self) -> list[Novel]:
        novels: list[dict[str, t.Any]] = await self._pool.find({}, {"_id": 0}).to_list(None)
        return [Novel.from_dict(novel) for novel in novels]

    async def get_novels_count(self) -> int:
        num: int = await self._pool.count_documents({})
        return num

    async def get_novel_id(self) -> int:
        self.current_count = await self.get_novels_count() if not self.current_count else self.current_count
        self.current_count += 1
        return self.current_count

    async def update(self, novel: Novel) -> None:
        await self._pool.update_one({"id": novel.id}, {"$set": novel.to_dict()})

    async def update_novel_id(self, novel_id: int, new_id: int) -> None:
        await self._pool.update_one({"id": novel_id}, {"$set": {"id": new_id}})

    @staticmethod
    def _make_match(
        title: str,
        rating: float,
        language: str,
        original_language: str,
        uploader: int | None,
        category: str,
        tag: str,
        size: float,
    ) -> dict[str, t.Any]:
        match: dict[str, t.Any] = {}
        if title:
            match["title"] = {"$regex": title, "$options": "i"}
        if rating:
            match["rating"] = {"$gte": rating}
        if language:
            match["language"] = language
        if original_language:
            match["original_language"] = original_language
        if uploader:
            match["uploader"] = uploader
        if category:
            match["category"] = category
        if tag:
            match["tags"] = {"$in": [tag]}
        if size:
            match["size"] = {"$gte": size}
        return match

    async def find_common(
        self,
        title: str = "",
        rating: float = 0.0,
        language: str = "",
        original_language: str = "",
        uploader: int | None = None,
        category: str = "",
        tag: str = "",
        size: float = 0.0,
    ) -> list[int]:
        common_ids = await self._pool.aggregate(
            [
                {"$match": self._make_match(title, rating, language, original_language, uploader, category, tag, size)},
                {"$project": {"id": 1}},
            ]
        ).to_list(None)
        return [common_id["id"] for common_id in common_ids]

    async def validate_position(self, title: str, language: str, size: float) -> int:
        common = await self.find_common(title=title, language=language)
        novels = await self.get_novels(common)
        for novel in novels:
            if novel.title == title and novel.language == language and novel.size <= size:
                return novel.id
        return await self.get_novel_id()

    async def get_random_novel(self) -> Novel:
        novel: dict[str, t.Any] = await self._pool.aggregate([{"$sample": {"size": 1}}]).next()
        return Novel.from_dict(novel)

    async def get_all_tags(self) -> list[str]:
        self.count = await self.get_novels_count() if not self.count else self.count
        if not self.tags:
            self.tags = await self._pool.distinct("tags")
        if self.count != await self.get_novels_count():
            self.tags = await self._pool.distinct("tags")
            self.count = await self.get_novels_count()
        return self.tags

    async def get_all_titles(self) -> list[str]:
        self.count = await self.get_novels_count() if not self.count else self.count
        if not self.titles:
            self.titles = await self._pool.distinct("title")
        if self.count != await self.get_novels_count():
            self.titles = await self._pool.distinct("title")
            self.count = await self.get_novels_count()
        return self.titles


class Warn:
    def __init__(self, pool: motor_asyncio.AsyncIOMotorDatabase) -> None:
        self._pool: motor_asyncio.AsyncIOMotorCollection = pool["warns"]

    async def get_log(self, user_id: int) -> WarnModel | None:
        user: dict[str, t.Any] | None = await self._pool.find_one({"id": user_id}, {"_id": 0})
        return WarnModel.from_dict(user) if user else None

    async def add_log(self, user_id: int, reason: str, blocked_by: int) -> None:
        user = await self.get_log(user_id)
        if user:
            return await self.update_log(user_id, reason, blocked_by)
        await self._pool.insert_one(
            WarnModel(id=user_id, warns=[LogModel(reason=reason, moderator=blocked_by)]).to_dict()
        )

    async def update_log(self, user_id: int, reason: str, blocked_by: int) -> None:
        await self._pool.update_one(
            {"id": user_id}, {"$push": {"warns": LogModel(reason=reason, moderator=blocked_by).to_dict()}}
        )

    async def update_warn(self, user_id: int, reason: str, blocked_by: int) -> None:
        user = await self.get_log(user_id)
        if not user:
            return await self.add_log(user_id, reason, blocked_by)
        await self.update_log(user_id, reason, blocked_by)

    async def remove_log(self, user_id: int) -> None:
        await self._pool.delete_one({"id": user_id})

    async def get_all_logs(self) -> list[WarnModel]:
        return [WarnModel.from_dict(user) async for user in self._pool.find({}, {"_id": 0})]

    async def blocked(self, user_id: int) -> bool:
        user: WarnModel | None = await self.get_log(user_id)
        data: dict[str, t.Any] = user.to_dict() if user else {}
        return bool(len(data.get("warns", [])) >= 3)
