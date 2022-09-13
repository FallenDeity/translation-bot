import os
import re

from motor import motor_asyncio

from databases.data import Novel


class Database:
    def __init__(self) -> None:
        self.db = motor_asyncio.AsyncIOMotorClient(os.getenv("DATABASE"))


class Library(Database):
    def __init__(self) -> None:
        super().__init__()
        self.library = self.db["library"]["data"]

    async def add_novel(self, data: Novel) -> None:
        await self.library.insert_one(data.__dict__)

    async def get_novel_by_id(self, _id: int) -> Novel:
        novel = await self.library.find_one({"_id": _id})
        return Novel(**novel) if novel else None

    async def update_novel(self, novel: Novel) -> None:
        await self.library.update_one({"_id": novel._id}, {"$set": novel.__dict__})

    async def get_novel_by_name(self, name: str) -> list[Novel]:
        novels = await self.library.find({"title": re.compile(name, re.IGNORECASE)}).to_list(None)
        return [Novel(**novel) for novel in novels] if novels else None

    async def get_novel_by_tags(self, tags: list[str]) -> list[Novel]:
        novels = await self.library.find({"tags": {"$in": tags}}).to_list(None)
        return [Novel(**novel) for novel in novels] if novels else None

    async def get_novel_by_language(self, language: str) -> list[Novel]:
        novels = await self.library.find({"language": language}).to_list(None)
        return [Novel(**novel) for novel in novels] if novels else None

    async def get_novel_by_rawlanguage(self, rawlanguage: str) -> list[Novel]:
        novels = await self.library.find({"org_language": rawlanguage}).to_list(None)
        return [Novel(**novel) for novel in novels] if novels else None

    async def get_novel_by_rating(self, rating: int) -> list[Novel]:
        novels = await self.library.find({"rating": {"$gte": rating - 1}}).to_list(None)
        return [Novel(**novel) for novel in novels] if novels else None

    async def get_novel_by_size(self, size: float) -> list[Novel]:
        size = int(size * 1024**2)
        novels = await self.library.find({"size": {"$gte": size}}).to_list(None)
        return [Novel(**novel) for novel in novels] if novels else None

    async def update_rating(self, _id: int, rating: int) -> None:
        await self.library.update_one({"_id": _id}, {"$set": {"rating": rating}})

    async def update_description(self, _id: int, description: str) -> None:
        await self.library.update_one(
            {"_id": _id}, {"$set": {"description": description}}
        )

    @property
    async def next_number(self) -> int:
        return await self.get_total_novels + 1

    @property
    async def get_all_novels(self) -> list:
        novels = await self.library.find().to_list(length=await self.get_total_novels)
        return [Novel(**novel) for novel in novels]

    @property
    async def get_all_tags(self) -> list[str]:
        tags = set([j for i in await self.get_all_novels for j in i.tags])
        return list(tags)

    @property
    async def get_all_titles(self) -> list[str]:
        titles = set([i.title for i in await self.get_all_novels])
        return list(titles)

    @property
    async def get_total_novels(self) -> int:
        return await self.library.count_documents({})
