import asyncio

import discord
from discord.ext import tasks

from core.bot import Raizel

bot = Raizel()


@tasks.loop(seconds=120)
async def census():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=f"{len(bot.users)} novel enthusiasts. Prefix: .t",
        ),
        status=discord.Status.idle,
    )


@census.before_loop
async def before_census():
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    print(f"Running as {bot.user}")
    


async def main():
    async with bot:
        print("done"


if __name__ == "__main__":
    asyncio.run(main())
