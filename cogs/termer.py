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
from languages.terms import terms
from utils.handler import FileHandler
from utils.translate import Translator


class Termer(commands.Cog):
    def __init__(self, bot: Raizel) -> None:
        self.bot = bot

    @staticmethod
    def term_raw(text, term_dict):
        for i in term_dict:
            text = text.replace(i, term_dict[i])
        return text

    @commands.hybrid_command(
        help="Replace terms in a text with the command. For large files use temp.sh. or mega.nz",
        aliases=["term"],
    )
    async def termer(
            self,
            ctx: commands.Context,
            term: str = None,
            link: str = None,
            file: typing.Optional[discord.Attachment] = None,
            messageid: str = None,
            language: str = "english",
            novelname: str = None,
            rawname: str = None,
            library_id: str = None,
    ):
        if link is not None and link.startswith("#"):
            try:
                novel_id = int(link.replace("#", ""))
                novel_data = await self.bot.mongo.library.get_novel_by_id(novel_id)
                link = novel_data.download
            except:
                return await ctx.reply("send a valid id")
        if library_id is not None:
            try:
                novel_data = await self.bot.mongo.library.get_novel_by_id(library_id)
                link = novel_data.download
            except:
                return await ctx.reply("send a valid id")
        file = link or file
        if not file and not messageid:
            return await ctx.reply(f"> **❌Send an attachment or a link.**")
        if ctx.author.id in self.bot.blocked:
            reason = await self.bot.mongo.blocker.get_banned_user_reason(ctx.author.id)
            reason = reason['reason']
            return await ctx.reply(
                content=f"You have been blocked by admins for improper usage of bot. Please contact admin \nReason : {reason}")
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
        if link is not None and ("discord.com/channels" in link or link.isnumeric()):
            messageid = link
            link = None
        if ctx.message.attachments and not str(link).startswith("https://cdn.discordapp.com"):
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
            file_type = path.suffix.replace(".", "")
            name = name.replace(".txt", "").replace(".docx", "").replace(".epub", "").replace(".pdf", "")
            if "txt" not in file_type and "docx" not in file_type and "epub" not in file_type:
                os.remove(path)
                await rep_msg.delete()
                return await ctx.send("> **❌Only .txt, .docx, .pdf and .epub supported**")
            name = name[:100]
            # os.rename(path, f"{ctx.author.id}.{file_type}")
            if "docx" in file_type:
                await FileHandler.docx_to_txt(ctx, file_type)
            if "epub" in file_type:
                await FileHandler.epub_to_txt(ctx)
            if "pdf" in file_type:
                await FileHandler.pdf_to_txt(ctx)
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
        if term is None:
            return await ctx.reply(
                f"**Please Choose the validterms to be applied :\n\t"
                f"1 : Naruto \n\t2 : One-Piece \n\t3 : Pokemon\n\t4 : Mixed anime terms\n\t"
                f"5 : Prince of Tennis\n\t6 : Anime + Marvel + DC\n\t7 : Cultivation terms\n\t"
                f"8 : encoding converter \t"
            )
        else:
            rep_msg = await rep_msg.edit(content=f"> **✅Terming started. **")
            term_dict = terms(term)
        if term_dict == {}:
            return await ctx.reply(
                f"**Please try again with the validterms to be applied :\n\t"
                f"1 : Naruto \n\t2 : One-Piece \n\t3 : Pokemon\n\t4 : Mixed anime terms\n\t"
                f"5 : Prince of Tennis\n\t6 : Anime + Marvel + DC\n\t7 : Cultivation terms\n\t"
            )
        if "discord" in link and "cdn.discord" not in link:
            if msg is None:
                msg = ctx.message
            resp = await self.bot.con.get(link)
            name = msg.attachments[0].filename.replace(".txt", "").replace(".docx", "").replace(".epub", "").replace(".pdf", "")
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
            name = link.split("/")[-1].replace(".txt", "").replace(".docx", "").replace(".epub", "").replace(".pdf", "")
            name = name.replace("%20", " ")
        if "plain" in file_type.lower() or "txt" in file_type.lower():
            file_type = "txt"
        elif "document" in file_type.lower() or "docx" in file_type.lower():
            file_type = "docx"
        elif "epub" in file_type.lower():
            file_type = "epub"
        elif "pdf" in file_type.lower():
            file_type = "pdf"
        else:
            return await ctx.send("> **❌Only .txt, .docx, .pdf and .epub supported**")
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
                chk_msg = await ctx.send(embed=discord.Embed(
                    description=f"This novel is already in our library... \nDo you want to search in library with ids {str(ids)}...react to this message with 🇾  ...\n If you want to continue translation react with 🇳"))
                await chk_msg.add_reaction('🇾')
                await chk_msg.add_reaction('🇳')

                def check(reaction, user):
                    return reaction.message.id == chk_msg.id and (
                                str(reaction.emoji) == '🇾' or str(reaction.emoji) == '🇳') and user == ctx.author

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
                    ctx.command = await self.bot.get_command("library search").callback(Library(self.bot), ctx, name,
                                                                                        language)
                    return None
                else:
                    await ctx.send("Reaction received", delete_after=10)
                    if str(res[0]) == '🇳':
                        pass
                    else:
                        try:
                            os.remove(f"{ctx.author.id}.txt")
                        except:
                            pass
                        ctx.command = await self.bot.get_command("library search").callback(Library(self.bot), ctx,
                                                                                            name, language)
                        return None
        if novel is None:
            data = await resp.read()
            async with aiofiles.open(f"{ctx.author.id}.{file_type}", "wb") as f:
                await f.write(data)
            if "docx" in file_type:
                await FileHandler.docx_to_txt(ctx, file_type)
            if "epub" in file_type:
                await FileHandler.epub_to_txt(ctx)
            if "pdf" in file_type:
                await FileHandler.pdf_to_txt(ctx)
            novel = await FileHandler().read_file(ctx)
        rep_msg = await rep_msg.edit(content=f"> **✅Terming started. **")
        novel = self.term_raw(novel, term_dict)
        msg_content = f"> **✅Terming completed ..Translation started. Translating to {language}.**"
        rep_msg = await rep_msg.edit(
            content=msg_content
        )
        try:
            os.remove(f"{ctx.author.id}.txt")
            original_Language = FileHandler.find_language(novel)
            liz = [novel[i: i + 1800] for i in range(0, len(novel), 1800)]
            self.bot.translator[ctx.author.id] = f"0/{len(liz)}"
            asyncio.create_task(self.cc_prog(rep_msg, msg_content, ctx.author.id))
            translate = Translator(self.bot, ctx.author.id, language)
            story = await translate.start(liz)
            async with aiofiles.open(f"{ctx.author.id}.txt", "w", encoding="utf-8") as f:
                await f.write(story)
            await FileHandler().distribute(self.bot, ctx, name, language, original_Language, raw_name=rawname)
        except Exception as e:
            if "Translation stopped" in str(e):
                return await ctx.send("Translation stopped")
            else:
                raise Exception
        finally:
            del self.bot.translator[ctx.author.id]
            self.bot.titles.append(name)
            self.bot.titles = random.sample(self.bot.titles, len(self.bot.titles))

    @termer.autocomplete("language")
    async def translate_complete(
            self, inter: discord.Interaction, language: str
    ) -> list[app_commands.Choice]:
        lst = [i for i in self.bot.all_langs if language.lower() in i.lower()][:25]
        return [app_commands.Choice(name=i, value=i) for i in lst]

    async def cc_prog(self, msg: discord.Message, msg_content: str, author_id: int) -> typing.Optional[discord.Message]:
        while author_id in self.bot.translator:
            await asyncio.sleep(6)
            if author_id not in self.bot.translator:
                return None
            content = msg_content + f"\nProgress > **🚄`{self.bot.translator[author_id]}`**"
            await msg.edit(content=content)
        return

    @termer.autocomplete("term")
    async def translate_complete(
            self, inter: discord.Interaction, term: str
    ) -> list[app_commands.Choice]:
        lst = [
                  "naruto",
                  "one-piece",
                  "pokemon",
                  "mixed",
                  "prince-of-tennis",
                  "marvel",
                  "dc",
                  "xianxia",
              ] + list(map(str, range(1, 8)))
        return [app_commands.Choice(name=i, value=i) for i in lst]

    @commands.hybrid_command(
        help="Clears any stagnant novels which were deposited for translation."
    )
    async def termclear(self, ctx):
        if ctx.author.id in self.bot.translator:
            del self.bot.translator[ctx.author.id]
        files = os.listdir()
        for i in files:
            if str(ctx.author.id) in str(i) and "crawl" not in i:
                os.remove(i)
        await ctx.reply("> **✔Cleared all records.**")


async def setup(bot):
    await bot.add_cog(Termer(bot))
