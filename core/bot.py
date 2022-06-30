import datetime
import os
import discord
import typing as t
from languages.languages import choices
from filestack import Client
from discord.ext import commands


class Raizel(commands.Bot):
    boot: datetime.datetime.utcnow()

    def __init__(self) -> None:
        intents = discord.Intents.all()
        self.translator: t.Dict[int, str] = {}
        self.crawler: t.Dict[int, str] = {}
        self.languages = choices
        super().__init__(command_prefix=commands.when_mentioned_or('.t'),
                         intents=intents,
                         strip_after_prefix=True,
                         case_insensitive=True,
                         help_command=None,
                         )

    async def _load_cogs(self, reload_if_loaded=False) -> None:
        if not reload_if_loaded:
            for extension in os.listdir("cogs"):
                if extension.endswith(".py") and extension[:2] != "__":
                    await self.load_extension(f"cogs.{extension[:-3]}")
                    print(f'Loaded {extension}')
            return
        for extension in os.listdir("cogs"):
            if extension.endswith(".py") and extension[:2] != "__":
                try:
                    await self.load_extension(f"cogs.{extension[:-3]}")
                except commands.ExtensionAlreadyLoaded:
                    await self.reload_extension(f"cogs.{extension[:-3]}")

    async def on_ready(self) -> None:
        print("Bot is online!")
        await self.setup_hook()

    async def setup_hook(self) -> None:
        await self._load_cogs()
        self.drive = Client(os.getenv('DRIVE'))
        return await super().setup_hook()

    async def start(self) -> None:
        return await super().start(os.getenv('TOKEN'), reconnect=True)

    @property
    def uptime(self) -> datetime.timedelta:
        return datetime.datetime.now() - self.boot

    @property
    def invite_url(self) -> str:
        return f"https://discord.com/api/oauth2/authorize?client_id={self.user.id}&permissions=8&scope=bot%20applications.commands"