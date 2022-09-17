import datetime
import os

import discord
import heroku3
from discord.ext import commands

from core import Raizel
from databases.blocked import User


class Admin(commands.Cog):
    def __init__(self, bot: Raizel) -> None:
        self.bot = bot

    @commands.has_role(1020638168237740042)
    @commands.hybrid_command(help="ban user")
    async def ban(self, ctx: commands.Context, id: str,
                  reason: str ="continuous use of improper names in novel name translation"):
        id = int(id)
        user_data = [
            id,
            reason,
            datetime.datetime.utcnow().timestamp(),
        ]
        user = User(*user_data)
        m_user = self.bot.get_user(id)
        await ctx.send(
            f"User {m_user.mention} banned due to {reason}"
        )

        await m_user.send(embed=discord.Embed(
            title="Blocked",
            description=f" You have been blocked by admins of @JARVIS bot due to {reason}\n",
            color=discord.Color.red(),
        ))
        await self.bot.mongo.blocker.ban(user)
        self.bot.blocked = await self.bot.mongo.blocker.get_all_banned_users()
        # await self.bot.mongo.blocker.get_all_banned_users()

    @commands.has_role(1020638168237740042)
    @commands.hybrid_command(help="Gives all the banned users")
    async def banned(self, ctx: commands.Context):
        await ctx.send("banned users")
        await self.bot.mongo.blocker.get_all_banned_users()
        self.bot.blocked = await self.bot.mongo.blocker.get_all_banned_users()
        await ctx.send(self.bot.blocked)

    @commands.has_role(1020638168237740042)
    @commands.hybrid_command(help="ban user")
    async def unban(self, ctx: commands.Context, id: str):
        id = int(id)
        user = self.bot.get_user(id)
        await user.send(embed=discord.Embed(
            title="Congrats",
            description=f" You have been unbanned by admins. Please follow the guidelines in future",
            color=discord.Color.blurple(),
        ))
        await ctx.send(
            f"Unbanned user : {user.mention}"
        )
        await self.bot.mongo.blocker.unban(id)
        self.bot.blocked = await self.bot.mongo.blocker.get_all_banned_users()

    @commands.has_role(1020638168237740042)
    @commands.hybrid_command(help="send warning to user")
    async def warn(self, ctx: commands.Context, id: int,
                   reason: str = "continuous use of improper names in novel name translation"):
        user = self.bot.get_user(id)
        await user.send(embed=discord.Embed(
            title="WARNING!!!",
            description=f" You have been warned by admins of @JARVIS bot due to {reason}\nIf you continue do so , you will be banned from using bot",
            color=discord.Color.yellow(),
        ))

    @commands.has_role(1020638168237740042)
    @commands.hybrid_command(help="send warning to user")
    async def get_id(self, ctx: commands.Context, name: str, discriminator: str):
        user = discord.utils.get(self.bot.get_all_members(), name=name, discriminator=discriminator)
        await ctx.send(f"{user.id}")

    @commands.has_role(1020638168237740042)
    @commands.hybrid_command()
    async def restart(self, ctx: commands.Context):
        await ctx.send(
            embed=discord.Embed(
                description=f"Bot is restarting...",
                color=discord.Color.random(),
            ),
        )
        h = heroku3.from_key(os.getenv("APIKEY"))
        app = h.app(os.getenv("APPNAME"))
        app.restart()


async def setup(bot):
    await bot.add_cog(Admin(bot))
