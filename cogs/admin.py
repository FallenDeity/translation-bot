import asyncio
import datetime
import gc
import os
import platform

import discord
from discord.ext import commands

from cogs.library import Library
from core import Raizel
from databases.blocked import User


def days_hours_minutes(td):
    return td.days, td.seconds // 3600, (td.seconds // 60) % 60


class Admin(commands.Cog):
    def __init__(self, bot: Raizel) -> None:
        self.bot = bot

    @commands.has_role(1020638168237740042)
    @commands.hybrid_command(help="ban user.. Admin only command")
    async def ban(self, ctx: commands.Context, id: str,
                  reason: str = "continuous use of improper names in novel name translation"):
        await ctx.defer()
        if '#' in id:
            name_spl = id.split('#')
            name = name_spl[0]
            discriminator = name_spl[1]
            user = discord.utils.get(self.bot.get_all_members(), name=name, discriminator=discriminator)
            id = user.id
        id = int(id)
        user_data = [
            id,
            reason,
            datetime.datetime.utcnow().timestamp(),
        ]
        user = User(*user_data)
        m_user = self.bot.get_user(id)
        try:
            await m_user.send(embed=discord.Embed(
                title="Blocked",
                description=f" You have been blocked by admins of @JARVIS bot due to {reason}\n",
                color=discord.Color.red(),
            ))
        except:
            pass
        await self.bot.mongo.blocker.ban(user)
        self.bot.blocked = await self.bot.mongo.blocker.get_all_banned_users()
        await ctx.send(
            f"User {m_user.mention} banned due to {reason}"
        )
        channel = self.bot.get_channel(
            991911644831678484
        ) or await self.bot.fetch_channel(991911644831678484)
        try:
            return await channel.send(embed=discord.Embed(
                description=f"User {m_user.name} has been banned by {ctx.author.name}",
                colour=discord.Color.dark_gold())
            )
        except:
            pass

    @commands.has_role(1020638168237740042)
    @commands.hybrid_command(help="Gives all the banned users.. Admin only command")
    async def banned(self, ctx: commands.Context):
        await ctx.send("banned users")
        await self.bot.mongo.blocker.get_all_banned_users()
        self.bot.blocked = await self.bot.mongo.blocker.get_all_banned_users()
        out = '\n'
        for block in self.bot.blocked:
            try:
                print(block)
                users: discord.User = self.bot.get_user(block)
                out = out + users.name + "#" + users.discriminator + "\t"
            except Exception as e:
                print(e)
        return await ctx.send("IDS : " + str(self.bot.blocked) + out)

    @commands.has_role(1020638168237740042)
    @commands.hybrid_command(help="Unban user.. Admin only command")
    async def unban(self, ctx: commands.Context, id: str):
        await ctx.defer()
        if '#' in id:
            name_spl = id.split('#')
            name = name_spl[0]
            discriminator = name_spl[1]
            user = discord.utils.get(self.bot.get_all_members(), name=name, discriminator=discriminator)
            id = user.id
        id = int(id)
        try:
            user = self.bot.get_user(id)
            await user.send(embed=discord.Embed(
                title="Congrats",
                description=f" You have been unbanned by admins. Please follow the guidelines in future",
                color=discord.Color.blurple(),
            ))
        except:
            pass
        await self.bot.mongo.blocker.unban(id)
        self.bot.blocked = await self.bot.mongo.blocker.get_all_banned_users()
        await ctx.send(
            f"Unbanned user : {user.mention}"
        )
        channel = self.bot.get_channel(
            991911644831678484
        ) or await self.bot.fetch_channel(991911644831678484)
        try:
            return await channel.send(embed=discord.Embed(
                description=f"User {user.name} has been unbanned by {ctx.author.name}",
                colour=discord.Color.dark_gold())
            )
        except:
            pass

    @commands.has_role(1020638168237740042)
    @commands.hybrid_command(help="send warning to user..Admin only command")
    async def warn(self, ctx: commands.Context, id: str,
                   reason: str = "continuous use of improper names in novel name translation"):
        await ctx.defer()
        if '#' in id:
            name_spl = id.split('#')
            name = name_spl[0]
            discriminator = name_spl[1]
            user = discord.utils.get(self.bot.get_all_members(), name=name, discriminator=discriminator)
            id = user.id
        id = int(id)
        user = self.bot.get_user(id)
        await user.send(embed=discord.Embed(
            title="WARNING!!!",
            description=f" You have been warned by admins of @JARVIS bot due to {reason}\nIf you continue do so , you will be banned from using bot",
            color=discord.Color.yellow(),
        ))
        return await ctx.reply(content=f"Warning has been sent to {user.mention}")

    @commands.has_role(1020638168237740042)
    @commands.hybrid_command(help="get id of the user if name and discriminator provided. Admin only command")
    async def get_id(self, ctx: commands.Context, name: str, discriminator: str = None):
        await ctx.defer()
        if '#' in name:
            name_spl = name.split('#')
            name = name_spl[0]
            discriminator = name_spl[1]
        user = discord.utils.get(self.bot.get_all_members(), name=name, discriminator=discriminator)
        return await ctx.send(content=f"{user.id}", ephemeral=True)

    @commands.has_role(1020638168237740042)
    @commands.hybrid_command(help="Restart the bot incase of bot crash. Ping any BOT-admins to restart bot")
    async def restart(self, ctx: commands.Context):
        try:
            await ctx.defer()
        except:
            pass
        msg = await ctx.send("Please wait")
        self.bot.app_status = "restart"
        while True:
            print("Started restart")
            if not self.bot.crawler.items() and not self.bot.translator.items():
                print("restart " + str(datetime.datetime.now()))
                channel = self.bot.get_channel(
                    991911644831678484
                ) or await self.bot.fetch_channel(991911644831678484)
                try:
                    await channel.send(embed=discord.Embed(description=f"Bot has started restarting"))
                except:
                    pass
                break
            else:
                print("waiting")
                self.bot.app_status = "restart"
                self.bot.translator = {}
                self.bot.crawler = {}
                await asyncio.sleep(40)

        await msg.edit(
            content="",
            embed=discord.Embed(
                description=f"Bot is restarting...",
                color=discord.Color.random(),
            ),
        )
        channel = self.bot.get_channel(
            991911644831678484
        ) or await self.bot.fetch_channel(991911644831678484)
        try:
            await channel.send(
                f"Bot has been restarted by user : {ctx.author.name} \nBot has translated {str(self.bot.translation_count)} novels and crawled {str(self.bot.crawler_count)} novels"
            )
            del self.bot.titles
            gc.collect()
        except:
            pass

        return await self.bot.start()
        # raise Exception("TooManyRequests")
        # h = heroku3.from_key(os.getenv("APIKEY"))
        # app = h.app(os.getenv("APPNAME"))
        # app.restart()

    @commands.guild_only()
    @commands.hybrid_command(help="Give the latency and uptime of the bot... ")
    async def status(self, ctx: commands.Context):
        # await ctx.send(str(datetime.datetime.utcnow())+".-"+str(ctx.message.created_at))
        await ctx.defer()
        embed = discord.Embed(title="Status", description="Status of the bot", color=discord.Color.dark_gold())
        embed.set_thumbnail(url=self.bot.user.avatar)
        embed.set_footer(text="Thanks for  using the bot!", icon_url=ctx.author.avatar)
        embed.add_field(name="Guilds", value=f"{len(self.bot.guilds)}", inline=True)
        embed.add_field(name="Users", value=f"{len(self.bot.users)}", inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        embed.add_field(name="OS", value=platform.system(), inline=True)
        try:
            embed.add_field(name="CPU usage", value=str(round(float(os.popen(
                '''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),
                                                         2)) + " %", inline=True)
            mem = str(os.popen('free -t -m').readlines())
            mem_G = mem[mem.index('T') + 14:-4]
            S1_ind = mem_G.index(' ')
            mem_G1 = mem_G[S1_ind + 8:]
            S2_ind = mem_G1.index(' ')
            mem_F = mem_G1[S2_ind + 8:]
            embed.add_field(name="RAM available", value=f"{mem_F} MB", inline=True)
        except Exception as e:
            print(e)
        admin = False
        for roles in ctx.author.roles:
            if roles.id == 1020638168237740042:
                admin = True
                embed1 = discord.Embed(title="Status", description="Status of the bot", color=discord.Color.dark_gold())
                embed1.set_thumbnail(url=self.bot.user.avatar)
                embed1.set_footer(text="Thanks for  using the bot!", icon_url=ctx.author.avatar)
                td = datetime.datetime.utcnow() - self.bot.boot
                td = days_hours_minutes(td)
                embed1.add_field(name="UpTime",
                                 value=f"{str(td[0]) + ' days ' if td[0] > 0 else ''}{str(td[1]) + 'hours ' if td[1] > 0 else ''}{str(td[2]) + ' minutes' if td[2] > 0 else ''}",
                                 inline=False)
                embed1.add_field(name="Tasks Completed", value=f"{str(self.bot.translation_count)} translated, "
                                                               f"{str(self.bot.crawler_count)} crawled", inline=False)
                embed1.add_field(name="Current Tasks", value=f"{len(self.bot.crawler)} Crawl,"
                                                             f" {len(self.bot.translator)} translate", inline=True)
                embed1.add_field(name="Tasks Count", value=str(len(asyncio.all_tasks())), inline=True)
        if admin:
            await Library.buttons([embed, embed1], ctx)
        else:
            await ctx.send(embed=embed)

    @commands.has_role(1020638168237740042)
    @commands.hybrid_command(help="Give the progress of all current tasks of the bot(only for bot-admins)... ")
    async def tasks(self, ctx: commands.Context):
        await ctx.defer()
        out = "**Crawler Tasks**\n"
        if not self.bot.crawler.items():
            out = out + "No tasks currently\n"
        else:
            for keys, values in self.bot.crawler.items():
                user = self.bot.get_user(keys)
                user = user.name
                out = f"{out}{user} : {values} \n"
        out = out + "\n**Translator Tasks**\n"
        if not self.bot.translator.items():
            out = out + "No tasks currently\n"
        else:
            for keys, values in self.bot.translator.items():
                user = self.bot.get_user(keys)
                user = user.name
                out = f"{out}{user} : {values} \n"
        return await ctx.send(embed=discord.Embed(description=out[:3800], colour=discord.Color.random()),
                              ephemeral=True)


async def setup(bot):
    await bot.add_cog(Admin(bot))
