import asyncio

import discord
from discord.ext import tasks
from utils.handler import FileHandler as handler

from core.bot import Raizel

bot = Raizel()
 

# @tasks.loop(seconds=60)
# async def census():
#     await handler.update_status(bot)
#     return


# @census.before_loop
# async def before_census():
#     await bot.wait_until_ready()


@bot.event
async def on_ready():
    print(f"Running as {bot.user}")
    await bot.tree.sync()
    # census.start()
    # bot.auto_restart.start()


async def main():
    async with bot:
        await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
