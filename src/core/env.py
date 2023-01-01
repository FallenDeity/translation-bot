import os
import typing as t
from dataclasses import dataclass

from dotenv import load_dotenv
from trafilatura.settings import use_config

# pyright: reportUnknownVariableType=false
load_dotenv()
# we need to do due to generic typing of load_dotenv


__all__: tuple[str, ...] = ("JARVIS",)


MISSING = object()


@dataclass(kw_only=True)
class Variable:
    name: str
    default: t.Any = MISSING
    cast: t.Callable[[str | t.Any], t.Any] = str

    def __post_init__(self) -> None:
        self.default = os.getenv(self.name, self.default)
        if self.default is MISSING:
            raise ValueError(f"Missing environment variable {self.name}")
        try:
            self.default = self.cast(self.default)
        except Exception as e:
            raise RuntimeError(f"Failed to cast {self.name} to {self.cast}") from e

    def __repr__(self) -> str:
        return f"{self.name}={self.default}"

    def __call__(self) -> t.Any:
        return self.default


class Environment:
    TOKEN: Variable = Variable(name="TOKEN")
    MONGO_URI: Variable = Variable(name="MONGO_URI")
    MEGA_EMAIL: Variable = Variable(name="MEGA_EMAIL")
    MEGA_PASSWORD: Variable = Variable(name="MEGA_PASSWORD")
    DETECT: Variable = Variable(name="DETECT", cast=lambda x: str(x).split())
    TRAFIL = use_config()
    TRAFIL.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")


JARVIS = Environment()
