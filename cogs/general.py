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

    @commands.hybrid_command(help="Give us a suggestion")
    async def suggestions(self, ctx: commands.Context, suggestion: str):
        """Give us a suggestion
                       Parameters
                       ----------
                       ctx : commands.Context
                           The interaction
                       suggestion :
                            Suggest a feature with explanation or report any bug
                       """
        channel = await self.bot.fetch_channel(1055445441958916167)
        embed = discord.Embed(title=f"{ctx.author.name}'s suggestion",
                              description=f"{suggestion}\n\nsuggested by {ctx.author.mention}",
                              url=ctx.author.default_avatar)
        await channel.send(embed=embed, allowed_mentions=discord.AllowedMentions(users=False))
        await ctx.send(content="Suggestion is sent to developer")


async def setup(bot: Raizel) -> None:
    await bot.add_cog(General(bot))
