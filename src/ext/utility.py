import disnake
import psutil
import os
import sys
from disnake.ext import commands, tasks

from src.core.views import InviteView
from src.utils import Eval

from . import Cog


class Utility(Cog):

    @tasks.loop(seconds=120)
    async def _update_status(self) -> None:
        total_novels = await self.bot.mongo.library.get_novels_count()
        await self.bot.change_presence(
            activity=disnake.Activity(
                type=disnake.ActivityType.watching,
                name=f"{total_novels} novels in library | {len(self.bot.users)} users",
            )
        )

    async def cog_load(self) -> None:
        await self.bot.wait_until_ready()
        self._update_status.start()

    @commands.slash_command(name="ping", description="Get the bot's latency.")
    async def ping(self, inter: disnake.ApplicationCommandInteraction) -> None:
        """Get the bot's latency."""
        await inter.response.send_message(f"Pong! {round(self.bot.latency * 1000)}ms")

    @commands.slash_command(name="invite", description="Get the bot's invite link.")
    async def invite(self, inter: disnake.ApplicationCommandInteraction) -> None:
        """Get the bot's invite link."""
        embed = disnake.Embed(
            title="Invite",
            description="**Invite the bot to your server!**",
            color=disnake.Color.random(),
        )
        embed.set_footer(text="Thanks for using TranslationBot!", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=inter.client.user.display_avatar)
        await inter.response.send_message(embed=embed, view=InviteView(self.bot))

    @commands.slash_command(name="stats", description="Get the bot's stats.")
    async def stats(self, inter: disnake.ApplicationCommandInteraction) -> None:
        """Get the bot's stats."""
        embed = disnake.Embed(
            title="Stats",
            description="**Stats of the bot!**",
            color=disnake.Color.random(),
        )
        embed.add_field(name="Guilds", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="Users", value=f"{len(self.bot.users)}", inline=True)
        embed.add_field(name="Commands", value=f"{len(self.bot.application_commands)}", inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Memory", value=f"{round(psutil.virtual_memory().available / 1024 ** 3)}GB", inline=True)
        embed.add_field(name="CPU", value=f"{psutil.cpu_percent()}%", inline=True)
        embed.set_footer(text="Thanks for using TranslationBot!", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=inter.client.user.display_avatar)
        await inter.response.send_message(embed=embed, view=InviteView(self.bot))

    @commands.message_command(name="Execute Code", description="Execute a python code")
    @commands.is_owner()
    async def exec(self, inter: disnake.ApplicationCommandInteraction, message: disnake.Message) -> None:
        """Execute python code"""
        code = message.content
        code = code.replace("```py", "").replace("```", "").strip()
        evaluator = Eval()
        renv = {
            "bot": self.bot,
            "inter": inter,
        }
        stdout, stderr = await evaluator.f_eval(code=code, renv=renv)
        string = ""
        if stdout:
            string += f"**Output**:\n```py\n{stdout}\n```\n"
        if stderr:
            string += f"**Error**:\n```py\n{stderr}\n```\n"
        await inter.send(content=string)

    @commands.slash_command(name="restart", description="Restart the bot")
    @commands.is_owner()
    async def restart(self, inter: disnake.ApplicationCommandInteraction) -> None:
        """Restart the bot"""
        await inter.response.send_message("Restarting...")
        os.execl(sys.executable, sys.executable, *sys.argv)
