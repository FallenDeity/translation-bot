import datetime
import typing

import discord
from discord.ext import commands

from core.bot import Raizel
from core.views.linkview import LinkView
from databases.data import Novel
from utils.category import Categories
from utils.handler import FileHandler


class General(commands.Cog):
    def __init__(self, bot: Raizel) -> None:
        self.bot = bot
        self.buttons = {
            "Invite": [self.bot.invite_url, "💖"],
            "Support Server": [
                "https://discord.gg/SZxTKASsHq",
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
        return await ctx.send(embed=embed, view=view)

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
        return await ctx.send(content="Suggestion is sent to developer")

    @commands.is_owner()
    @commands.hybrid_command(help="command to add role for storage access. only owner")
    async def addrole(self, ctx: commands.Context):
        await ctx.send("started adding roles")
        n = await self.bot.add_roles()
        return await ctx.send(f"added storage-access role to {n} users")

    @commands.hybrid_command(help="add novel to library")
    async def addnovel(self, ctx: commands.Context, file: typing.Optional[discord.Attachment] = None, link: str = None, name: str = ""):
        if file is None and link is None:
            await ctx.reply("add a file or link")

        if file:
            link = file.url
            if name.strip() == "":
                name = file.filename.replace(".txt", "").replace(".docx", "").replace(".epub", "").replace(".pdf", "")
        category = Categories.from_string(name)
        no = await self.bot.mongo.library.next_number
        novel_data = [
            no,
            name,
            "",
            0,
            "english",
            await FileHandler.get_tags(name),
            link,
            999999,
            ctx.author.id,
            datetime.datetime.now(datetime.timezone.utc).timestamp(),
            # datetime.datetime.utcnow().timestamp(),
            Categories.thumbnail_from_category(category),
            "english",
            category,
            link
        ]
        data = Novel(*novel_data)
        try:
            await self.bot.mongo.library.add_novel(data)
            await ctx.send(f"> added to bot with library id {no}")
        except:
            await ctx.send("couldn't add to library try again")




async def setup(bot: Raizel) -> None:
    await bot.add_cog(General(bot))
