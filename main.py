import asyncio

import aiohttp
import discord
from discord.ext import tasks

from core.bot import Raizel

bot = Raizel()


@tasks.loop(seconds=120)
async def census():
    await bot.wait_until_ready()
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=f"{len(bot.users)} novel enthusiasts. Prefix: .t",
        ),
        status=discord.Status.idle,
    )


@bot.event
async def on_ready():
    print(f"Running as {bot.user}")
    census.start()


async def main():
    async with aiohttp.ClientSession() as session:
        async with bot:
            bot.con = session
            await bot.start()


asyncio.run(main())
