import os
import sys

import disnake
import psutil
from disnake.ext import commands, tasks

from src.core.views import InviteView
from src.core.views.paginators import Paginator
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
        embed.add_field(name="Memory", value=f"{round(psutil.virtual_memory().available / 1024 ** 2)}MB", inline=True)
        embed.add_field(name="CPU", value=f"{psutil.cpu_percent()}%", inline=True)
        embed.set_footer(text="Thanks for using TranslationBot!", icon_url=self.bot.user.avatar)
        embed.set_thumbnail(url=inter.client.user.display_avatar)
        await inter.response.send_message(embed=embed, view=InviteView(self.bot))

    @commands.slash_command(name="leaderboard", description="Get the bot's leaderboard.")
    async def leaderboard(self, inter: disnake.ApplicationCommandInteraction) -> None:
        """Get the bot's leaderboard."""
        await inter.response.defer()
        user_rank = await self.bot.mongo.library.get_user_novel_count(inter.author.id)
        top_200 = await self.bot.mongo.library.get_user_novel_count(_top_200=True)
        embeds = []
        top_200 = [(user_id, count) for user_id, count in top_200.items()]
        chunks = [top_200[i : i + 10] for i in range(0, len(top_200), 10)]
        n = 1
        for chunk in chunks:
            embed = disnake.Embed(
                title="Leaderboard",
                description=f"**Leaderboard of the bot!**\
                    \n\n**Your Rank:** {user_rank[inter.author.id]}",
                color=disnake.Color.random(),
            )
            embed.set_footer(text="Thanks for using TranslationBot!", icon_url=self.bot.user.display_avatar)
            embed.set_thumbnail(url=inter.client.user.display_avatar)
            for user_id, count in chunk:
                embed.add_field(
                    name=f"{n}. {count} novels",
                    value=f"<@{user_id}>",
                    inline=False,
                )
                n += 1
            embeds.append(embed)
        await Paginator.paginate(inter, self.bot, embeds)

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

    @commands.slash_command(name="suggest", description="Suggest a feature")
    async def suggest(self, inter: disnake.ApplicationCommandInteraction, *, suggestion: str) -> None:
        """Suggest a feature

        Parameters
        ----------
        inter : disnake.ApplicationCommandInteraction
            The interaction
        suggestion: str
            The suggestion.
        """
        channel = self.bot.get_channel(1055445441958916167) or await self.bot.fetch_channel(1055445441958916167)
        assert isinstance(channel, disnake.TextChannel)
        embed = disnake.Embed(
            title="Suggestion",
            description=f"```fix\n{suggestion}\n```",
            color=disnake.Color.random(),
        )
        embed.set_footer(text=f"From {inter.author}", icon_url=inter.author.display_avatar)
        await channel.send(embed=embed)
        await inter.response.send_message("Suggestion sent!", ephemeral=True)
