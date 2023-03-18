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

    @commands.is_owner()
    @commands.hybrid_command(help="Give us a suggestion")
    async def addrole(self, ctx: commands.Context):
        guild = self.bot.get_guild(940866934214373376)
        role = guild.get_role(1076124121592770590)
        await ctx.send("started adding roles")
        top = await self.bot.mongo.library.get_user_novel_count(_top_200=True)
        top_200 = [(user_id, count) for user_id, count in top.items()]
        chunks = [top_200[i: i + 10] for i in range(0, len(top_200), 10)]
        user_ids = []
        no = 0
        for chunk in chunks:
            for user_id, count in chunk:
                if count >= 10:
                    user_ids.append(user_id)
        members = guild.members
        for member in members:
            if member.id in user_ids:
                no = no + 1
                print(f"added role to {member.name}")
                await member.add_roles(role)
            else:
                print(f"not adding access to  {member.name}")

        await ctx.send(f"added  roles to {no}")


async def setup(bot: Raizel) -> None:
    await bot.add_cog(General(bot))
