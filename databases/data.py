import datetime
from dataclasses import dataclass
# from typing import List


@dataclass
class Novel:
    _id: int
    title: str
    description: str
    rating: float
    language: str
    tags: list[str]
    download: str
    size: float
    uploader: int
    date: datetime.datetime.timestamp
    thumbnail: str = "https://cdn.discordapp.com/attachments/1055445441958916167/1055780604655964210/image0.jpg"
    org_language: str = 'NA'
    category: str = 'others'
    crawled_from: str = None
