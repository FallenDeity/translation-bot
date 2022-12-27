import dataclasses
import datetime
import typing as t

__all__: tuple[str, ...] = (
    "Warn",
    "Novel",
    "Log",
)


@dataclasses.dataclass
class Log:
    reason: str
    moderator: int
    timestamp: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.now)

    @classmethod
    def from_dict(cls, data: dict[str, t.Any]) -> "Log":
        return cls(
            reason=data.get("reason", ""),
            moderator=data.get("moderator", 0),
        )

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "reason": self.reason,
            "moderator": self.moderator,
            "timestamp": self.timestamp,
        }


@dataclasses.dataclass
class Warn:
    id: int
    warns: list[Log] = dataclasses.field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, t.Any]) -> "Warn":
        return cls(
            id=data.get("id", 0),
            warns=[Log.from_dict(log) for log in data.get("warns", [])],
        )

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "id": self.id,
            "warns": [log.to_dict() for log in self.warns],
        }


@dataclasses.dataclass
class Novel:
    id: int
    title: str
    description: str
    thumbnail: str
    rating: float
    language: str
    original_language: str
    tags: list[str]
    download: str
    size: float
    uploader: int
    category: str
    crawled_source: str
    date: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.now)

    @classmethod
    def from_dict(cls, data: dict[str, t.Any]) -> "Novel":
        return cls(
            id=data.get("id", 0),
            title=data.get("title", ""),
            description=data.get("description", ""),
            thumbnail=data.get("thumbnail", ""),
            rating=data.get("rating", 0),
            language=data.get("language", ""),
            tags=data.get("tags", []),
            download=data.get("download", ""),
            size=data.get("size", 0),
            uploader=data.get("uploader", 0),
            category=data.get("category", ""),
            date=data.get("date", datetime.datetime.now()),
            crawled_source=data.get("crawled_source", ""),
            original_language=data.get("original_language", data.get("language", "")),
        )

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "thumbnail": self.thumbnail,
            "rating": self.rating,
            "language": self.language,
            "tags": self.tags,
            "download": self.download,
            "size": self.size,
            "uploader": self.uploader,
            "date": self.date,
            "category": self.category,
            "crawled_source": self.crawled_source,
            "original_language": self.original_language,
        }
