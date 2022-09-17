import datetime
from dataclasses import dataclass


@dataclass
class User:
    userid: int
    reason: str
    date: datetime.datetime.timestamp