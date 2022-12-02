import datetime
from dataclasses import dataclass
from typing import List


@dataclass
class Novel:
    _id: int
    title: str
    description: str
    rating: float
    language: str
    tags: List[str]
    download: str
    size: float
    uploader: int
    date: datetime.datetime.timestamp
    org_language: str = 'NA'
