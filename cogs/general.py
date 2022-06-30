import datetime
from core.bot import Raizel
import discord
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot: Raizel) -> None:
        self.bot = bot

    @commands.command(help="Invite command to invite the bot to your server.")
    async def invite(self, ctx):
        embed = discord.Embed(title="Invite",
                              description=f"**📱Invite {self.bot.user.name} to your server.**",
                              colour=discord.Colour.random())
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        view = discord.ui.View()
        invite = discord.ui.Button(label="Invite", style=discord.ButtonStyle.link, emoji="💖", url=self.bot.invite_url)
        server = discord.ui.Button(label="Support Server", style=discord.ButtonStyle.link, emoji=self.bot.get_emoji(952146686338285588), url='https://discord.gg/EN3ECMHEZP')
        view.add_item(invite)
        view.add_item(server)
        await ctx.send(embed=embed, view=view)


async def setup(bot: Raizel) -> None:
    await bot.add_cog(General(bot))