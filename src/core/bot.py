import datetime
import importlib
import inspect
import os
import pathlib
import sys
import traceback
import typing as t

import aiohttp
import disnake
import dotenv
from disnake.ext import commands
from mega import Mega

from ..assets import Termer
from ..database import Database
from .logger import Logger

__all__: tuple[str, ...] = ("TranslationBot",)
dotenv.load_dotenv()


class TranslationBot(commands.InteractionBot):
    def __init__(
        self,
        *args: t.Any,
        log_channel: int = 1012229238415433768,
        extensions: str | pathlib.Path = "src/ext",
        **kwargs: t.Any,
    ) -> None:
        super().__init__(*args, **kwargs, intents=disnake.Intents.default())
        self.extension_path = pathlib.Path(extensions)
        self.log_channel = log_channel
        self.logger = Logger(name="TranslationBot", extention="bot")
        self.termer = Termer()
        self._uptime = datetime.datetime.utcnow()
        self.http_session = aiohttp.ClientSession()
        self.mongo = Database(self.logger)
        self.mega = Mega().login(email=os.getenv("MEGA_EMAIL"), password=os.getenv("MEGA_PASSWORD"))
        self.logger.flair("Logged in to Mega!")

    def run(self, *args: t.Any, **kwargs: t.Any) -> None:
        self.logger.info("Loading extensions...")
        self._load_all_extensions()
        self.logger.info("Loaded all extensions!")
        try:
            super().run(os.environ["TOKEN"], *args, **kwargs)
        except (KeyboardInterrupt, KeyError):
            self.logger.critical("Failed to run the bot!")
            self.logger.info("Closed!")

    async def on_error(self, event_method: str, *args: t.Any, **kwargs: t.Any) -> None:
        error = "".join(traceback.format_exception(*sys.exc_info()))
        self.logger.error(f"Error in {event_method}: {error}")

    async def on_ready(self) -> None:
        self.logger.flair(f"Logged in as {self.user} ({self.user.id})")

    async def close(self) -> None:
        self.logger.info("Closing...")
        await self.http_session.close()
        await super().close()
        self.logger.info("Closed!")

    def _auto_setup(self, path: str) -> None:
        module = importlib.import_module(path)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, commands.Cog) and name != "Cog":
                self.add_cog(obj(self))

    def _load_all_extensions(self) -> None:
        for extension in self.extension_path.glob("*.py"):
            if extension.name.startswith("_"):
                continue
            self._auto_setup(f"{self.extension_path.parent}.{self.extension_path.name}.{extension.stem}")
            self.logger.info(f"Loaded {extension.stem} extension!")

    @property
    def invite_url(self) -> str:
        return f"https://discord.com/oauth2/authorize?client_id={self.user.id}" \
               f"&scope=applications.commands%20bot&permissions=8"

    @property
    def uptime(self) -> float:
        return (datetime.datetime.utcnow() - self._uptime).total_seconds()
