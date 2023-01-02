import datetime
import importlib
import inspect
import pathlib
import sys
import traceback
import typing as t

import aiohttp
import disnake
import mega
import nltk
from disnake.ext import commands

from ..assets import Termer
from ..database import Database
from .env import JARVIS
from .logger import Logger

__all__: tuple[str, ...] = ("TranslationBot",)


class TranslationBot(commands.InteractionBot):
    def __init__(
        self,
        *args: t.Any,
        log_channel: int = 991911644831678484,
        extensions: str | pathlib.Path = "src/ext",
        **kwargs: t.Any,
    ) -> None:
        super().__init__(
            *args, **kwargs, intents=disnake.Intents.all(), owner_ids={656838010532265994, 772129808544432140}
        )
        self.config = JARVIS
        self.extension_path = pathlib.Path(extensions)
        self.log_channel = log_channel
        self.logger = Logger(name="TranslationBot", extention="bot")
        self.termer = Termer()
        self._uptime = datetime.datetime.now()
        self.http_session = aiohttp.ClientSession()
        self.mongo = Database(self.logger, token=self.config.MONGO_URI())
        self._login_mega()
        self.logger.flair("Logged in to Mega!")

    def _login_mega(self) -> None:
        try:
            self.mega = mega.Mega()
            self.mega.login(self.config.MEGA_EMAIL(), self.config.MEGA_PASSWORD())
        except mega.mega.RequestError:
            self.logger.critical("Failed to login to Mega!")
            self.mega = mega.Mega().login()

    def run(self, *args: t.Any, **kwargs: t.Any) -> None:
        self.logger.info("Loading nltk")
        nltk.download("brown")
        nltk.download("punkt")
        nltk.download("popular")
        self.logger.info("Loaded nltk")
        self.logger.info("Loading extensions...")
        self._load_all_extensions()
        self.logger.info("Loaded all extensions!")
        try:
            super().run(self.config.TOKEN(), *args, **kwargs)
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
        return (
            f"https://discord.com/oauth2/authorize?client_id={self.user.id}"
            f"&scope=applications.commands%20bot&permissions=8"
        )

    @property
    def uptime(self) -> float:
        return (datetime.datetime.now() - self._uptime).total_seconds()
