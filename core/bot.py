import datetime
import os
import random
import typing as t

import aiohttp
import discord
import nltk
from discord.ext import commands
from filestack import Client
from mega import Mega

from languages.languages import choices
from languages.sites import sites
from languages.terms import get_dictionary
from utils.connector import Mongo


class Raizel(commands.Bot):
    con: aiohttp.ClientSession
    boot: datetime.datetime.utcnow()
    allowed: list[str]
    drive: Client
    mongo: Mongo

    def __init__(self) -> None:
        self.titles: list = None
        self.blocked = None
        self.mega: Mega 
        intents = discord.Intents.all()
        self.translator: t.Dict[int, str] = {}
        self.crawler: t.Dict[int, str] = {}
        self.languages = choices
        self.dictionary: str = get_dictionary()
        super().__init__(
            command_prefix=commands.when_mentioned_or(".t"),
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
                    print(f"Loaded {extension}")
            return
        for extension in os.listdir("cogs"):
            if extension.endswith(".py") and extension[:2] != "__":
                try:
                    await self.load_extension(f"cogs.{extension[:-3]}")
                except commands.ExtensionAlreadyLoaded:
                    await self.reload_extension(f"cogs.{extension[:-3]}")

    async def setup_hook(self) -> None:
        nltk.download("brown")
        nltk.download("punkt")
        nltk.download("popular")
        await self._load_cogs()
        await self.load_extension("jishaku")
        self.allowed = sites
        self.con = aiohttp.ClientSession()
        self.drive = Client(os.getenv("FILE"))
        self.mongo = Mongo()
        print("Connected to mongo db")
        self.blocked: list[int] = await self.mongo.blocker.get_all_banned_users()
        self.titles = list(await self.mongo.library.get_all_titles)
        print("Loaded titles")
        self.titles = random.sample(self.titles, len(self.titles))
        try:
            self.mega = Mega().login(os.getenv("USER"), os.getenv("MEGA"))
            print("Connected to Mega")
        except Exception as e:
            try:
                self.mega = Mega().login()
                print("mega connection failed... connected anonymously")
            except:
                print("mega login anonymouly failed ..Please check pasword or account status")
            print(e)
        # await self.tree.sync()
        return await super().setup_hook()

    async def start(self) -> None:
        return await super().start(os.getenv("TOKEN"), reconnect=True)

    @property
    def uptime(self) -> datetime.timedelta:
        return datetime.datetime.now() - self.boot

    @property
    def invite_url(self) -> str:
        return f"https://discord.com/api/oauth2/authorize?client_id={self.user.id}&permissions=8&scope=bot%20applications.commands"

    @property
    def display_langs(self) -> str:
        string = ["{0: ^17}".format(f"{k} --> {v}") for k, v in self.languages.items()]
        string = "\n".join(
            ["".join(string[i : i + 3]) for i in range(0, len(string), 3)]
        )
        return string

    @property
    def all_langs(self) -> list[str]:
        langs = list(self.languages.keys()) + list(self.languages.values())
        return langs
