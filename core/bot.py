import asyncio
import datetime
import gc
import os
import random
import traceback
import joblib
import typing as t

import aiohttp
import discord
import nltk
from discord.ext import commands
from mega import Mega

from languages.languages import choices
from languages.sites import sites
from languages.terms import get_dictionary
from utils.connector import Mongo
from discord.ext import tasks


class Raizel(commands.Bot):
    con: aiohttp.ClientSession
    boot: datetime.datetime.utcnow()
    allowed: list[str]
    # drive: Client
    mongo: Mongo

    def __init__(self) -> None:
        self.blocked = None
        self.mega: Mega = None
        intents = discord.Intents.all()
        self.translator: t.Dict[int, str] = {}
        self.crawler: t.Dict[int, str] = {}
        self.languages = choices
        self.dictionary: list[str] = get_dictionary()
        self.boot = datetime.datetime.utcnow()
        self.app_status: str = "up"
        self.translation_count: float = 0
        self.crawler_count = 0
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
        try:
            await self._load_cogs()
            await self.load_extension("jishaku")
        except Exception as e:
            print(traceback.print_exc())
            print("cogs already loaded")
        self.allowed = sites
        self.con = aiohttp.ClientSession()
        # self.drive = Client(os.getenv("FILE"))
        self.mongo = Mongo()
        print("Connected to mongo db")
        self.blocked: list[int] = await self.mongo.blocker.get_all_banned_users()
        channel = await self.fetch_channel(991911644831678484)
        try:
            self.mega = Mega().login(os.getenv("USER"), os.getenv("MEGA"))
            print("Connected to Mega")
        except Exception as e:
            try:
                self.mega = Mega().login()
                await channel.send(f"> <@&1020638168237740042> **Couldn't connect with Mega. some problem occured "
                                   f"with mega account**\n{e}", allowed_mentions=discord.AllowedMentions(roles=False))
                print("mega connection failed...connected anonymously....Please check password or account status")
            except:
                await channel.send(
                    f"> <@&1020638168237740042> **Couldn't connect with Mega servers. "
                    f"some problem with connection \n{e}",
                    allowed_mentions=discord.AllowedMentions(roles=False))
                print("mega login anonymously failed ..something wrong with mega", )
            print(e)
        # await self.tree.sync()
        await channel.send(embed=discord.Embed(description=f"Bot is up now"))
        return await super().setup_hook()

    async def load_title(self):
        print("started loading titles")
        try:
            titles = list(dict.fromkeys(list(await self.mongo.library.get_all_distinct_titles)))
            titles = random.sample(titles, len(titles))
            joblib.dump(titles, 'titles.sav')
            print("Loaded titles")
            del titles
            return
        except Exception as e:
            print("error loading titles")
            print(e)

    async def start(self) -> None:
        try:
            return await super().start(os.getenv("TOKEN"), reconnect=True)
        except Exception as e:
            try:
                await super().close()
            except:
                pass
            print('error occurred on connecting to Discord client... will try after 60 secs')
            print(e)
            # time.sleep(60)
            # return await self.start()

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
            ["".join(string[i: i + 3]) for i in range(0, len(string), 3)]
        )
        return string

    @property
    def all_langs(self) -> list[str]:
        langs = list(self.languages.keys()) + list(self.languages.values())
        return langs

    @tasks.loop(hours=2)
    async def auto_restart(self):
        if self.auto_restart.current_loop == 0:
            asyncio.create_task(self.load_title())
        i = 0
        if self.auto_restart.current_loop != 0:
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name="for Restart. Please don't start any other tasks till I turn idle",
                ),
                status=discord.Status.do_not_disturb,
            )
            self.app_status = "restart"
            self.translator = {}
            self.crawler = {}
            await asyncio.sleep(50)
            while True:
                print("Started restart")
                if (not self.crawler.items() and not self.translator.items()) or i == 20:
                    print("restart " + str(datetime.datetime.now()))
                    try:
                        for x in os.listdir():
                            if x.endswith("txt") and "requirements" not in x:
                                print(f"deleting {x}")
                                os.remove(x)
                            if "titles.sav" in x:
                                os.remove(x)
                    except Exception as e:
                        print("exception occurred  in deleting")
                        await channel.send(f"error occurred in deleting {x} {e}")
                    channel = self.get_channel(
                        991911644831678484
                    ) or await self.bot.fetch_channel(991911644831678484)
                    try:
                        await channel.send(embed=discord.Embed(
                            description=f"Bot has been auto-restarted. \nBot has "
                                        f"translated {str(int(self.translation_count*3.1))}MB novels and"
                                        f" crawled {str(self.crawler_count)} novels"
                            , colour=discord.Colour.brand_green()))
                        del self.titles
                        gc.collect()
                    except:
                        pass
                    try:
                        await self.close()
                        raise Exception
                        # new_ch = self.get_channel(
                        #     991911644831678484
                        # ) or await self.bot.fetch_channel(991911644831678484)
                        # msg_new = await new_ch.fetch_message(1050579735840817202)
                        # context_new = await self.bot.get_context(msg_new)
                        # command = await self.get_command("restart").callback(Admin(self), context_new)
                    except Exception as e:
                        await self.close()
                        raise Exception("closed session")
                        print("error occurred at restarting")
                        print(e)
                    break
                else:
                    i = i + 1
                    print("there are tasks waiting....")
                    channel = self.get_channel(
                        991911644831678484
                    ) or await self.bot.fetch_channel(991911644831678484)
                    await channel.send(embed=discord.Embed(
                        description="Task is already running.. waiting for it to finish for restart",
                        colour=discord.Colour.random()))
                    self.bot.translator = {}
                    self.bot.crawler = {}
                    await asyncio.sleep(60)
