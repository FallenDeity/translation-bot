import disnake
from disnake.ext import commands

from src.core.views import InviteView

from . import Cog


class Utility(Cog):
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
        embed.set_thumbnail(url=inter.client.user.display_avatar)
        await inter.response.send_message(embed=embed, view=InviteView(self.bot))
