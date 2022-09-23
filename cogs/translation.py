import asyncio
import os
import random
import typing

import aiofiles
import discord
from deep_translator import GoogleTranslator
from discord import app_commands
from discord.ext import commands

from cogs.library import Library
from core.bot import Raizel
from core.views.linkview import LinkView
from utils.handler import FileHandler
from utils.translate import Translator


class Translate(commands.Cog):
    def __init__(self, bot: Raizel) -> None:
        self.bot = bot

    @commands.hybrid_command(
        help="Gives progress of novel translation.", aliases=["now", "n", "p"]
    )
    async def progress(self, ctx: commands.Context):
        if ctx.author.id not in self.bot.translator:
            return await ctx.send(
                "> **❌You have no novel deposited for translation currently.**",
                delete_after=5,
            )
        await ctx.send(f"> **🚄`{self.bot.translator[ctx.author.id]}`**")

    @commands.hybrid_command(
        help="Send file to be translated with the command. For large files use temp.sh. or mega.nz",
        aliases=["t"],
    )
    async def translate(
            self,
            ctx: commands.Context,
            link: str = None,
            file: typing.Optional[discord.Attachment] = None,
            messageid: str = None,
            language: str = "english",
            novelname: str = None,
            rawname: str = None,
    ):
        file = link or file
        if ctx.author.id in self.bot.blocked:
            reason = await self.bot.mongo.blocker.get_banned_user_reason(ctx.author.id)
            reason = reason['reason']
            return await ctx.reply(content=f"You have been blocked by admins for improper usage of bot. Please contact admin \nReason : {reason}")
        if not file and not messageid:
            return await ctx.reply(f"> **❌Send an attachment or a link.**")
        if language not in self.bot.all_langs and "http" not in language:
            return await ctx.reply(
                f"**❌We have the following languages in our db.**\n```ini\n{self.bot.display_langs}```"
            )
        language = FileHandler.get_language(language)
        if ctx.author.id in self.bot.translator:
            return await ctx.send("> **❌You cannot translate two novels at a time.**")
        if not ctx.message.attachments and not file and messageid is None:
            return await ctx.send("> **❌You must add a novel/link to translate**")
        msg = None
        novel = None
        file_type = None
        name = None
        rep_msg = await ctx.reply("Please wait.. Translation will began soon")
        if ctx.message.attachments:
            link = ctx.message.attachments[0].url
        elif messageid is None and ("mega.nz" in link or "mega.co.nz" in link):
            await ctx.send("Mega link found.... downloading from mega", delete_after=5)
            info = self.bot.mega.get_public_url_info(link)
            size = int(info.get("size")) / 1000
            if size >= 15 * 1000:
                await rep_msg.delete()
                return await ctx.reply(
                    "> **❌ File size is too big... Please split the file and translate"
                )
            name = info.get("name")
            name = bytes(name, encoding="raw_unicode_escape", errors="ignore").decode()
            file_type = name.split(".")[-1]
            path = self.bot.mega.download_url(
                link, dest_filename=f"{ctx.author.id}.{file_type}"
            )
            if "txt" not in file_type and "docx" not in file_type:
                os.remove(path)
                await rep_msg.delete()
                return await ctx.send("> **❌Only .docx and .txt supported**")
            name = name.replace(".txt", "").replace(".docx", "")
            name = name[:100]
            # os.rename(path, f"{ctx.author.id}.{file_type}")
            if "docx" in file_type:
                await FileHandler.docx_to_txt(ctx, file_type)
            novel = await FileHandler.read_file(FileHandler, ctx=ctx)
        else:
            if messageid is not None:
                if 'discord' in messageid:
                    spl_link = messageid.split('/')
                    server_id = int(spl_link[4])
                    channel_id = int(spl_link[5])
                    msg_id = int(spl_link[6])
                    server = self.bot.get_guild(server_id)
                    channel = server.get_channel(channel_id)
                    resolvedMessage = await channel.fetch_message(msg_id)
                else:
                    channel = self.bot.get_channel(ctx.channel.id)
                    resolvedMessage = await channel.fetch_message(messageid)
                msg = resolvedMessage
                link = resolvedMessage.attachments[0].url
            elif isinstance(file, discord.Attachment):
                link = file.url
            else:
                link = file
        if "discord" in link:
            resp = await self.bot.con.get(link)
            if msg is None:
                msg = ctx.message
            name = msg.attachments[0].filename.replace(".txt", "").replace(".docx", "")
            file_type = resp.headers["content-type"].split("/")[-1]
        elif novel is None:
            resp = await self.bot.con.get(link)
            try:
                file_type = FileHandler.get_headers(resp)
            except KeyError:
                view = LinkView({"Storage": ["https://temp.sh", "📨"]})
                await rep_msg.delete()
                return await ctx.send(
                    "> **❌Currently this link is not supported.**", view=view
                )
            name = link.split("/")[-1].replace(".txt", "").replace(".docx", "")
            name = name.replace("%20", " ")
        if "plain" in file_type.lower() or "txt" in file_type.lower():
            file_type = "txt"
        elif "document" in file_type.lower() or "docx" in file_type.lower():
            file_type = "docx"
        else:
            return await ctx.send("> **❌Only .docx and .txt supported**")
        if novelname is not None:
            name = novelname
        name_check = FileHandler.checkname(name, self.bot)
        if rawname is not None:
            if not name_check:
                try:
                    name = GoogleTranslator(
                        source="auto", target="english"
                    ).translate(rawname).strip()
                    name_check = FileHandler.checkname(name, self.bot)
                except:
                    pass
        if not name_check:
            await rep_msg.delete()
            return await ctx.reply(
                f"> **❌{name} is not a valid novel name. please provide a valid name to filename before translating. **"
            )
        for tag in ['/', '\\', '<', '>', "'", '"', ':', ";", '?', '|', '*', ';', '!']:
            name = name.replace(tag, '').strip()
        name = name.replace('_', ' ')
        if novel is None:
            data = await resp.read()
            async with aiofiles.open(f"{ctx.author.id}.{file_type}", "wb") as f:
                await f.write(data)
            if "docx" in file_type:
                await FileHandler.docx_to_txt(ctx, file_type)
            novel = await FileHandler().read_file(ctx)
        novel_data = await self.bot.mongo.library.get_novel_by_name(name)
        if novel_data is not None:
            novel_data = list(novel_data)
            ids = []
            lang_check = False
            for n in novel_data:
                ids.append(n._id)
                if language == n.language:
                    lang_check = True
            if lang_check:
                ids = ids[:20]
                chk_msg = await ctx.send(embed=discord.Embed(description=f"This novel is already in our library with ids {str(ids)}...  \nDo you want to search in library...react to this message with 🇾  ...\nIf you want to continue translation react with 🇳"))
                await chk_msg.add_reaction('🇾')
                await chk_msg.add_reaction('🇳')

                def check(reaction, user):
                    return reaction.message.id == chk_msg.id and (str(reaction.emoji) == '🇾' or str(reaction.emoji) == '🇳') and user == ctx.author
                try:
                    res = await self.bot.wait_for(
                        "reaction_add",
                        check=check,
                        timeout=15.0,
                    )
                except asyncio.TimeoutError:
                    print('error')
                    try:
                        os.remove(f"{ctx.author.id}.txt")
                    except:
                        pass
                    await ctx.send("No response detected. sending novels in library", delete_after=10)
                    ctx.command = await self.bot.get_command("library search").callback(Library(self.bot), ctx, name, language)
                    return None
                else:
                    await ctx.send("Reaction received", delete_after=10)
                    if str(res[0]) == '🇳':
                        await chk_msg.delete()
                        pass
                    else:
                        try:
                            os.remove(f"{ctx.author.id}.txt")
                        except:
                            pass
                        ctx.command = await self.bot.get_command("library search").callback(Library(self.bot), ctx, name, language)
                        return None

        await rep_msg.edit(content=f"> **✅Translation started. Translating to {language}.**")
        try:
            try:
                original_Language = FileHandler.find_language(novel)
            except:
                original_Language = 'NA'
            os.remove(f"{ctx.author.id}.txt")
            liz = [novel[i: i + 1800] for i in range(0, len(novel), 1800)]
            self.bot.translator[ctx.author.id] = f"0/{len(liz)}"
            translate = Translator(self.bot, ctx.author.id, language)
            story = await translate.start(liz)
            async with aiofiles.open(f"{ctx.author.id}.txt", "w", encoding="utf-8") as f:
                await f.write(story)
            await FileHandler().distribute(self.bot, ctx, name, language, original_Language, rawname)
        except Exception as e:
            raise e
        finally:
            del self.bot.translator[ctx.author.id]
            self.bot.titles.append(name)
            # print(self.bot.titles[-1])
            self.bot.titles = random.sample(self.bot.titles, len(self.bot.titles))

    @translate.autocomplete("language")
    async def translate_complete(
            self, inter: discord.Interaction, language: str
    ) -> list[app_commands.Choice]:
        lst = [i for i in self.bot.all_langs if language.lower() in i.lower()][:25]
        return [app_commands.Choice(name=i, value=i) for i in lst]

    @commands.hybrid_command(
        help="Clears any stagnant novels which were deposited for translation."
    )
    async def tclear(self, ctx: commands.Context):
        if ctx.author.id in self.bot.translator:
            del self.bot.translator[ctx.author.id]
        files = os.listdir()
        for i in files:
            if str(ctx.author.id) in str(i) and "crawl" not in i:
                os.remove(i)
        await ctx.reply("> **✔Cleared all records.**")


async def setup(bot):
    await bot.add_cog(Translate(bot))

