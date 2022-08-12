import datetime

import discord
from discord.ext import commands

from core.bot import Raizel
from core.views.linkview import LinkView


class General(commands.Cog):
    def __init__(self, bot: Raizel) -> None:
        self.bot = bot
        self.buttons = {
            "Invite": [self.bot.invite_url, "💖"],
            "Support Server": [
                "https://discord.gg/EN3ECMHEZP",
                self.bot.get_emoji(952146686338285588),
            ],
        }

    @commands.hybrid_command(help="Invite command to invite the bot to your server.")
    async def invite(self, ctx):
        embed = discord.Embed(
            title="Invite",
            description=f"**📱Invite {self.bot.user.name} to your server.**",
            colour=discord.Colour.random(),
        )
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        view = LinkView(self.buttons)
        await ctx.send(embed=embed, view=view)


async def setup(bot: Raizel) -> None:
    await bot.add_cog(General(bot))
