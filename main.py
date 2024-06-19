import asyncio
import os

import discord
from discord.ext import commands
from discord.ext import tasks

from cogs.admin import Admin
from utils.handler import FileHandler as handler

from core.bot import Raizel

bot = Raizel()


@tasks.loop(minutes=10)
async def census():
    if census.current_loop > 15:
        chan = bot.get_channel(
            991911644831678484
        ) or await bot.fetch_channel(991911644831678484)
        msg_new2 = await chan.fetch_message(1052750970557308988)
        context_new2 = await bot.get_context(msg_new2)
        await chan.send("> Bot restart started with looper")
        command = await bot.get_command("restart").callback(Admin(bot), context_new2)
    await handler.update_status(bot)
    return


@census.before_loop
async def before_census():
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    print(f"Running as {bot.user}")
    await bot.tree.sync()
    census.start()
    # bot.auto_restart.start()


@bot.event
async def on_command(ctx: commands.Context):
    bot.logger.info(
        f"Command {ctx.command if ctx.command else 'Unknown Command'} called by {ctx.author} in {ctx.channel} with args {ctx.args} and kargs {ctx.kwargs}")


async def main():
    async with bot:
        await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
