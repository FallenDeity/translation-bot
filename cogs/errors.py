import os
import random
import traceback

import discord
import heroku3
from discord.ext import commands

from core.bot import Raizel


class ErrorHandler(commands.Cog):
    def __init__(self, bot: Raizel) -> None:
        self.bot = bot

    @staticmethod
    def underline(text, at, for_):
        underline = (" " * at) + ("^" * for_)
        return text + "\n" + underline

    @staticmethod
    def signature_parser(cmd) -> str:
        command_signature = ""
        for arg in cmd.signature.split(" ")[: len(cmd.params) - 2]:
            if "=" in arg:
                parsed_arg = "{" + arg.split("=")[0].strip("[]<>]") + "}"
            else:
                parsed_arg = "[" + arg.strip("[]<>") + "]"
                if parsed_arg == "[]":
                    parsed_arg = ""
            command_signature += parsed_arg + " "
        return command_signature

    @staticmethod
    def perms_parser(perms: list) -> str:
        return f"`{'` , `'.join(perms).title().replace('guild', 'server').replace('_', ' ')}`"

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error: Exception):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            desc = f"{ctx.prefix}{ctx.command.name} {ctx.command.signature}"
            print(error.param.name)
            inside = self.underline(
                desc, desc.index(f"{error.param.name}"), len(f"{error.param.name}")
            )
            desc = f"\n```ini\n{inside}\n```"
            await ctx.send(
                embed=discord.Embed(
                    description=f"Seems like you didn't provide a required argument : `{error.param.name}`{desc}",
                    color=discord.Color.red(),
                )
            )
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send(
                embed=discord.Embed(
                    description=f"Unable to find a role named `{error.argument}`",
                    color=discord.Color.red(),
                )
            )
        elif isinstance(error, commands.CommandOnCooldown):
            cooldown_embed = discord.Embed(
                title=random.choice(
                    [
                        "Slow down!",
                        "You're going a little too fast bud...",
                        "Hold your horses!",
                        "Noooooo!",
                        "Woah now, slow it down...",
                        "Take a breather...",
                        "NEGATORY.",
                    ]
                ),
                description=f"This command is on a cooldown! try again in `{round(error.retry_after, 2)}` seconds.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=cooldown_embed)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    description=f"You are missing `{self.perms_parser(error.missing_permissions)}` permissions required to run the command",
                    color=discord.Color.red(),
                ),
            )
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    description=f"I am missing `{self.perms_parser(error.missing_permissions)}` permissions required to run the command",
                    color=discord.Color.red(),
                )
            )
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(
                embed=discord.Embed(
                    description=f"Unable to find any member named `{error.argument}` in `{ctx.guild.name}`",
                    color=discord.Color.red(),
                )
            )
        elif isinstance(error, commands.UserNotFound):
            await ctx.send(
                embed=discord.Embed(
                    description=f"Unable to find a user named `{error.argument}`",
                    color=discord.Color.red(),
                )
            )

        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send(
                embed=discord.Embed(
                    description=f"No channel named `{error.argument}` found",
                    color=discord.Color.red(),
                )
            )
        elif isinstance(error, commands.MissingRole):
            await ctx.send(
                embed=discord.Embed(
                    description=f"You need `{error.missing_role}` role in order to use this command",
                    color=discord.Color.red(),
                )
            )
        elif isinstance(error, commands.NotOwner):
            await ctx.send(
                embed=discord.Embed(
                    title="No No",
                    description=f"`{ctx.command.name}` is an owner only command , only bot owner(s) can use it",
                    color=discord.Color.red(),
                )
            )
        elif isinstance(error, commands.TooManyArguments):
            await ctx.send(
                embed=discord.Embed(
                    title=f"Too many arguments provided , **Usage :** ```\nini{ctx.prefix} {ctx.command.name} {self.signature_parser(ctx.command)}\n```",
                    color=discord.Color.red(),
                )
            )
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(
                embed=discord.Embed(
                    description="This command is disabled", color=discord.Color.red()
                )
            )
        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.send(
                embed=discord.Embed(
                    description=f"`{ctx.command.name}` can be used only in DMs",
                    color=discord.Color.red(),
                )
            )
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(
                embed=discord.Embed(
                    description=f"`{ctx.command.name}` command cannot be used in DMs",
                    color=discord.Color.red(),
                )
            )
        elif isinstance(error, commands.MissingRequiredAttachment):
            await ctx.send(
                embed=discord.Embed(
                    description=f"You need to provide an attachment to use this command",
                    color=discord.Color.red(),
                )
            )
        elif isinstance(error, commands.BadArgument):
            await ctx.send(
                embed=discord.Embed(
                    description=f"You have provided wrong values in bot command. please use .thelp for help\n{str(error)}",
                    color=discord.Color.red(),
                )
            )
        elif "TooManyRequests" in str(error):
            await ctx.send(
                embed=discord.Embed(
                    description=f"Google translate limit reached. Trying to restart server",
                    color=discord.Color.red(),
                ),
            )
            h = heroku3.from_key(os.getenv("APIKEY"))
            app = h.app(os.getenv("APPNAME"))
            await ctx.send("> Bot is restarting... please try after 30 sec....")
            app.restart()
        elif "Error R14" in str(error):
            try:
                await ctx.send(
                    embed=discord.Embed(
                        description=f"Ram is overloaded .. trying to restart.",
                        color=discord.Color.red(),
                    ),
                )
            except:
                pass
            h = heroku3.from_key(os.getenv("APIKEY"))
            app = h.app(os.getenv("APPNAME"))
            await ctx.send("> Bot is restarting... please try after 30 sec....")
            app.restart()
        else:
            print(error)
            await ctx.send(
                "An unexpected error occurred! Reporting this to my developer..."
            )
            channel = self.bot.get_channel(
                991911644831678484
            ) or await self.bot.fetch_channel(991911644831678484)
            try:
                await channel.send(
                    f"```yaml\n{''.join(traceback.format_exception(error, error, error.__traceback__))}\n```"
                )
            except:
                await channel.send(str(error))
                await channel.send(error.__traceback__[:4000])
            raise error


async def setup(bot: Raizel) -> None:
    await bot.add_cog(ErrorHandler(bot))
