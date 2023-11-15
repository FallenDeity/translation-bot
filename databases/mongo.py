import os
import re
from datetime import datetime
from typing import Any

from motor import motor_asyncio

from databases.blocked import User
from databases.data import Novel
from utils.handler import FileHandler as fe


class Database:
    def __init__(self) -> None:
        self.db = motor_asyncio.AsyncIOMotorClient(os.getenv("DATABASE"))




class Library(Database):
    def __init__(self) -> None:
        super().__init__()
        self.library = self.db["library"]["data"]

    async def add_novel(self, data: Novel) -> None:
        await self.library.insert_one(data.__dict__)

    @staticmethod
    async def _make_match(
            title: str,
            rating: float,
            language: str,
            original_language: str,
            uploader: int,
            category: str,
            tag: str,
            size: float,
    ) -> dict[str, Any]:
        match: dict[str, Any] = {}
        if title:
            for subString in ["completed", "ongoing", "complete", "latest", "updated"]:
                title = str(re.sub('(?i)' + re.escape(subString), lambda k: "", title))
            title = await fe.get_regex_from_name(title)
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
            match["category"] = {"$regex": category, "$options": "i"}
        if tag:
            match["tags"] = {"$in": [tag]}
        if size:
            size = int(size * 1024 ** 2)
            match["size"] = {"$gte": size}
        return match

    async def find_common(
            self,
            title: str = "",
            rating: float = 0.0,
            language: str = "",
            original_language: str = "",
            uploader: int = None,
            category: str = "",
            tag: str = "",
            size: float = 0.0,
            no: int = 300,
    ) -> list[Novel]:
        commons = await self.library.aggregate(
            [
                {"$match": await self._make_match(title, rating, language, original_language, uploader, category, tag, size)},
                {"$sample": {"size": no}}
            ]
        ).to_list(None)
        return commons

    async def get_novel_by_id(self, _id: int) -> Novel:
        novel = await self.library.find_one({"_id": _id})
        return novel if novel else None

    async def get_title_by_id(self, _id: int) -> Novel:
        novel = await self.library.find_one({"_id": _id})
        return novel['title']

    async def get_uploader_by_id(self, _id: int):
        novel = await self.library.find_one({"_id": _id})
        return novel['uploader']

    async def get_random_novel(self, no: int = 10, language: str = "english"):
        novel = await self.library.aggregate([
            {"$match": {"language": language}},
            {"$sample": {"size": no}}]).to_list(None)
        return novel

    async def update_novel(self, novel: Novel) -> None:
        await self.library.update_one({"_id": novel._id}, {"$set": novel.__dict__})

    async def get_novel_by_name(self, name: str) -> list[Novel]:
        name = await fe.get_regex_from_name(name)
        novels = await self.library.find({"title": re.compile(name, re.IGNORECASE)}).to_list(None)
        return [Novel(**novel) for novel in novels] if novels else None

    async def get_novel_by_category(self, category: str) -> list[Novel]:
        novels = await self.library.find({"category": re.compile(category, re.IGNORECASE)}).to_list(None)
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
        size = int(size * 1024 ** 2)
        novels = await self.library.find({"size": {"$gte": size}}).to_list(None)
        return [Novel(**novel) for novel in novels] if novels else None

    async def get_novel_by_uploader(self, uploader: int) -> list[Novel]:
        novels = await self.library.find({"uploader": uploader}).to_list(None)
        return [Novel(**novel) for novel in novels] if novels else None

    async def update_rating(self, _id: int, rating: int) -> None:
        await self.library.update_one({"_id": _id}, {"$set": {"rating": rating}})

    async def update_category(self, _id: int, category: str) -> None:
        await self.library.update_one({"_id": _id}, {"$set": {"category": category}})

    async def update_description(self, _id: int, description: str) -> None:
        await self.library.update_one(
            {"_id": _id}, {"$set": {"description": description}}
        )

    async def update_download(self, _id: int, download: str) -> None:
        await self.library.update_one(
            {"_id": _id}, {"$set": {"download": download}}
        )

    async def update_thumbnail(self, _id: int, thumbnail: str) -> None:
        await self.library.update_one(
            {"_id": _id}, {"$set": {"thumbnail": thumbnail}}
        )

    async def update_size(self, _id: int, size: int) -> None:
        await self.library.update_one(
            {"_id": _id}, {"$set": {"size": size}}
        )

    async def update_date(self, _id: int, date: float) -> None:
        await self.library.update_one(
            {"_id": _id}, {"$set": {"date": date}}
        )

    async def update_novel_(self, _id: int, title: str, description: str, download: str, size: float,
                            date: datetime.timestamp
                            , thumbnail: str, category: str, crawled_from: str) -> None:
        await self.library.update_one(
            {"_id": _id}, {"$set": {"title": title, "description": description, "download": download, "size": size,
                                    "date": date, "thumbnail": thumbnail, "category": category,
                                    "crawled_from": crawled_from}}
        )

    async def get_user_novel_count(self, user_id: int = None, _top_200: bool = False) -> dict[int, int]:
        if user_id is None:
            top_200_uploaders = await self.library.aggregate(
                [
                    {"$group": {"_id": "$uploader", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 200},
                ]
            ).to_list(None)
            return {top_200_uploader["_id"]: top_200_uploader["count"] for top_200_uploader in top_200_uploaders}
        count = await self.library.count_documents({"uploader": user_id})
        user_rank = await self.library.aggregate(
            [
                {"$group": {"_id": "$uploader", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gt": count}}},
                {"$count": "count"},
            ]
        ).to_list(None)
        return {user_id: user_rank[0]["count"] + 1 if user_rank else 1}

    @property
    async def next_number(self) -> int:
        return await self.get_total_novels + 1

    @property
    async def get_all_novels(self) -> list:
        novels = await self.library.find().to_list(length=await self.get_total_novels)
        return [Novel(**novel) for novel in novels]

    @property
    async def get_all_tags(self) -> list[str]:
        tags = await self.library.distinct("tags")
        return tags

    @property
    async def get_all_distinct_titles(self) -> list[str]:
        titles = await self.library.distinct("title")
        return titles

    @property
    async def get_total_novels(self) -> int:
        return await self.library.count_documents({})


class Blocker(Database):
    def __init__(self) -> None:
        super().__init__()
        self.blocker = self.db["Blocker"]["blocked"]

    async def deleteall(self):
        await self.blocker.delete_many({'userid': {'$gte': 1000}})
        print('deleted all')

    async def ban(self, user: User) -> None:
        print(user)
        i = await self.blocker.insert_one(user.__dict__)
        print(i)
        print('user banned')

    async def unban(self, userid: int) -> None:
        await self.blocker.delete_one({"userid": userid})

    async def get_banned_user_reason(self, userid: int):
        temp = await self.blocker.find_one({"userid": userid})
        print(temp)
        return temp

    async def get_all_banned_users(self) -> list[int]:
        users = await self.blocker.find().to_list(length=await self.blocker.count_documents({}))
        users_id = [i['userid'] for i in users]
        return users_id
