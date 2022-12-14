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


def term_raw(text, term_dict):
    for i in term_dict:
        text = text.replace(i, term_dict[i])
    return text


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
            library_id: int = None,
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
        if self.bot.app_status == "restart":
            return await ctx.reply(f"> Bot is scheduled to restart within 60 sec or after all current tasks are completed.. Please try after bot is restarted")
        if ctx.author.id == 925597069748621353:
            while len(asyncio.all_tasks())>=10 or (ctx.author.id in self.bot.translator and not self.bot.translator[ctx.author.id] == "waiting"):
                if ctx.author.id not in self.bot.translator:
                    self.bot.translator[ctx.author.id] = f"waiting"
                await asyncio.sleep(20)
                if self.bot.translator[ctx.author.id] == "waiting" and len(self.bot.translator) <=1:
                    break
        file = link or file
        if ctx.author.id in self.bot.blocked:
            reason = await self.bot.mongo.blocker.get_banned_user_reason(ctx.author.id)
            reason = reason['reason']
            return await ctx.reply(
                content=f"You have been blocked by admins for improper usage of bot. Please contact admin \nReason : {reason}")
        if not file and not messageid:
            return await ctx.reply(f"> **❌Send an attachment or a link.**", )
        if language not in self.bot.all_langs and "http" not in language:
            return await ctx.reply(
                f"**❌We have the following languages in our db.**\n```ini\n{self.bot.display_langs}```"
            )
        language = FileHandler.get_language(language)
        if ctx.author.id in self.bot.translator and not ctx.author.id == 925597069748621353:
            return await ctx.send("> **❌You cannot translate two novels at a time.**", ephemeral=True)
        if not ctx.message.attachments and not file and messageid is None:
            return await ctx.send("> **❌You must add a novel/link to translate**", ephemeral=True)
        msg = None
        novel = None
        file_type = None
        name = None
        rep_msg = await ctx.reply("Please wait.. Translation will began soon")
        no_tries = 0
        while len(asyncio.all_tasks()) >= 9 or len(self.bot.translator) >= 3:
            no_tries = no_tries + 1
            try:
                rep_msg = await rep_msg.edit(
                    content=f"> **Currently bot is busy.Please wait some time. Please wait till bot become free. will retry automatically in 20sec  ** {str(no_tries)} try")
            except:
                pass
            if no_tries >= 5:
                self.bot.translator = {}
                if len(self.bot.translator) < 2:
                    break
                await asyncio.sleep(10)
            await asyncio.sleep(10)
        if link is not None and ("discord.com/channels" in link or link.isnumeric()):
            messageid = link
            link = None
        if ctx.message.attachments and not str(link).startswith("https://cdn.discordapp.com"):
            link = ctx.message.attachments[0].url
        elif messageid is None and ("mega.nz" in link or "mega.co.nz" in link):
            await ctx.send("Mega link found.... downloading from mega", delete_after=10, ephemeral=True)
            info = self.bot.mega.get_public_url_info(link)
            size = int(info.get("size")) / 1000
            if size >= 21 * 1000:
                await rep_msg.delete()
                return await ctx.reply(
                    "> **❌ File size is too big... Please split the file and translate**"
                )
            name = info.get("name")
            name = bytes(name, encoding="raw_unicode_escape", errors="ignore").decode()
            file_type = name.split(".")[-1]
            path = self.bot.mega.download_url(
                link, dest_filename=f"{ctx.author.id}.{file_type}"
            )
            if "txt" not in file_type and "docx" not in file_type and "epub" not in file_type and "pdf" not in file_type:
                os.remove(path)
                await rep_msg.delete()
                return await ctx.send("> **❌Only .txt, .docx, .pdf and .epub supported**", ephemeral=True)
            name = name.replace(".txt", "").replace(".docx", "").replace(".epub", "").replace(".pdf", "")
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
                try:
                    link = resolvedMessage.attachments[0].url
                except:
                    return await ctx.reply("> **There is no attachment in the provided message**")
            elif isinstance(file, discord.Attachment):
                link = file.url
            else:
                link = file
        if "discord" in link and "cdn.discord" not in link:
            resp = await self.bot.con.get(link)
            if msg is None:
                msg = ctx.message
            name = msg.attachments[0].filename.replace(".txt", "").replace(".docx", "").replace(".epub", "").replace(
                ".pdf", "")
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
            return await ctx.send("> **❌Only .txt, .docx , .pdf and .epub supported**", ephemeral=True)
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
            if "epub" in file_type:
                await FileHandler.epub_to_txt(ctx)
            if "pdf" in file_type:
                await FileHandler.pdf_to_txt(ctx)
            novel = await FileHandler().read_file(ctx)
        novel_data = await self.bot.mongo.library.get_novel_by_name(name)
        if novel_data is not None:
            novel_data = list(novel_data)
            ids = []
            lang_check = False
            eng_check = False
            size_check = False
            name_lib_check = False
            for n in novel_data:
                ids.append(n._id)
                if "english" == str(n.language).lower():
                    eng_check = True
                if language == str(n.language).lower():
                    lang_check = True
                    org_str = ''.join(e for e in name.split('__')[0] if e.isalnum())
                    lib_str = ''.join(e for e in str(n.title).split('__')[0] if e.isalnum())
                    if org_str.lower() in lib_str.lower() or org_str.lower() == lib_str.lower():
                        name_lib_check = True
                        try:
                            size_found = round(os.path.getsize(f"{ctx.author.id}.txt") / (1024 ** 2), 2) - 0.10
                            size_found = size_found - 0.1*size_found
                            lib_size = round(n.size / (1024 ** 2), 2)
                            if size_found <= lib_size <= 2*size_found:
                                size_check = True
                        except:
                            pass
            if lang_check:
                ids = ids[:20]
                rep_msg = await rep_msg.edit(content="Novel is already in our library")
                ctx.command = await self.bot.get_command("library search").callback(Library(self.bot), ctx, name,
                                                                                    language, None, None, None, None,
                                                                                    None, None, False, "size", 20)
                if len(ids) < 5 or name_lib_check:
                    await ctx.send("**Please check from above library**", delete_after=20)
                    await asyncio.sleep(15)
                if name_lib_check and size_check:
                    await ctx.send("**Please check from above library**")
                    return None
                chk_msg = await ctx.send(embed=discord.Embed(
                    description=f"This novel **{name}** is already in our library with ids **{str(ids)}**...use arrow marks  in above  to navigate...\nIf you want to continue translation react with 🇳 within 10 sec\n\n**Note : Some files are in docx format, so file size maybe half the size of txt. and try to minimize translating if its already in library**"))
                await chk_msg.add_reaction('🇾')
                await chk_msg.add_reaction('🇳')

                def check(reaction, user):
                    return reaction.message.id == chk_msg.id and (
                            str(reaction.emoji) == '🇾' or str(reaction.emoji) == '🇳') and user == ctx.author

                try:
                    res = await self.bot.wait_for(
                        "reaction_add",
                        check=check,
                        timeout=8.0,
                    )
                except asyncio.TimeoutError:
                    print('error')
                    try:
                        os.remove(f"{ctx.author.id}.txt")
                    except:
                        pass
                    await ctx.send("No response detected. ", delete_after=5)
                    await chk_msg.delete()
                    return None
                else:
                    if str(res[0]) == '🇳':
                        await rep_msg.delete()
                        rep_msg = await ctx.reply("Reaction received.. please wait")
                    else:
                        await ctx.send("Reaction received", delete_after=10)
                        try:
                            os.remove(f"{ctx.author.id}.txt")
                        except:
                            pass
                        await chk_msg.delete()
                        return None
        if (novel_data is None or not eng_check) and not language.lower() == "english":
            new_ch = self.bot.get_channel(
                942513122177073222
            ) or await self.bot.fetch_channel(942513122177073222)
            msg_new = await new_ch.fetch_message(1040971784742248509)
            context_new = await self.bot.get_context(msg_new)
            try:
                asyncio.create_task(self.bot.get_command("translate").callback(Translate(self.bot), context_new, link,
                                                                               file,
                                                                               None,
                                                                               "english", novelname, rawname,
                                                                               library_id))
            except:
                pass
        if ctx.author.id in self.bot.translator and not ctx.author.id == 925597069748621353:
            return await ctx.send("> **❌You cannot translate two novels at a time.**", ephemeral=True)
        msg_content = f"> **✅ Started translating 📔 {name}. Translating to {language}.**"
        rep_msg = await rep_msg.edit(content=msg_content)
        try:
            try:
                original_Language = FileHandler.find_language(novel)
            except:
                original_Language = 'NA'
            os.remove(f"{ctx.author.id}.txt")
            poke_words = ["elves ", "pokemon", "pokémon", " elf "]
            if any(word in name.lower() for word in poke_words):
                term_dict = terms("pokemon")
                novel = term_raw(novel, term_dict)
                await ctx.send("Added pokemon terms", delete_after=5)
            liz = [novel[i: i + 1800] for i in range(0, len(novel), 1800)]
            self.bot.translator[ctx.author.id] = f"0/{len(liz)}"
            asyncio.create_task(self.cc_prog(rep_msg, msg_content, ctx.author.id))
            translate = Translator(self.bot, ctx.author.id, language)
            story = await translate.start(liz)
            async with aiofiles.open(f"{ctx.author.id}.txt", "w", encoding="utf-8") as f:
                await f.write(story)
            await FileHandler().distribute(self.bot, ctx, name, language, original_Language, rawname)
        except Exception as e:
            if "Translation stopped" in str(e):
                return await ctx.send("Translation stopped")
            else:
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

    async def cc_prog(self, msg: discord.Message, msg_content: str, author_id: int) -> typing.Optional[discord.Message]:
        value = 0
        while author_id in self.bot.translator:
            await asyncio.sleep(8)
            if author_id not in self.bot.translator:
                content = msg_content + f"\nProgress > **🚄`Completed`    {100}%**"
                msg = await msg.edit(content=content)
                return None
            try:
                if eval(self.bot.translator[author_id]) < value:
                    content = msg_content + f"\nProgress > **🚄`Completed`    {100}%**"
                    msg = await msg.edit(content=content)
                    return None
                else:
                    value = eval(self.bot.translator[author_id])
                    out = str(round(value * 100, 2))
            except Exception as e:
                print(e)
                out = ""
            content = msg_content + f"\nProgress > **🚄`{self.bot.translator[author_id]}`    {out}%**"
            msg = await msg.edit(content=content)
        return

    @commands.hybrid_command(
        help="translate multiple files together one at a time"
    )
    async def multi(self, ctx: commands.Context, language: str = "english", messageid: int = None, ):
        if messageid:
            channel = self.bot.get_channel(ctx.channel.id)
            message = await channel.fetch_message(messageid)
        else:
            message = ctx.message
        if ctx.author.id in self.bot.blocked:
            reason = await self.bot.mongo.blocker.get_banned_user_reason(ctx.author.id)
            reason = reason['reason']
            return await ctx.reply(
                content=f"You have been blocked by admins for improper usage of bot. Please contact admin \nReason : {reason}")
        if language not in self.bot.all_langs:
            return await ctx.reply(
                f"**❌We have the following languages in our db.**\n```ini\n{self.bot.display_langs}```"
            )
        language = FileHandler.get_language(language)
        if not message.attachments:
            return await ctx.reply(content="> Attach a file to translate")
        count = 1
        for attached in message.attachments:
            try:
                ctx_new = await self.bot.get_context(message)
            except:
                channel = self.bot.get_channel(ctx_new.channel.id)
                message = await channel.fetch_message(messageid)
                ctx_new = await self.bot.get_context(message)
            await asyncio.sleep(1)
            await ctx_new.send(f"**Translating {count} out of {len(message.attachments)}**")
            count = count + 1
            await asyncio.sleep(0.5)
            try:
                ctx.command = await self.bot.get_command("translate").callback(Translate(self.bot), ctx_new, attached.url,
                                                                               None,
                                                                               None,
                                                                               language)
                await asyncio.sleep(5)
            except Exception as e:
                if "TooManyRequests" in str(e):
                    raise e
                else:
                    print(e)
                    ctx_new = self.bot.get_context(message)
                    await ctx_new.send(f"> Error occurred in translating {attached.filename}\ndue to : {str(e)}")

    @multi.autocomplete("language")
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
        try:
            await ctx.message.delete()
        except:
            pass
        for i in files:
            if str(ctx.author.id) in str(i) and "crawl" not in i:
                os.remove(i)
        await ctx.send(f">{ctx.author.mention} **✔Cleared all records.**", ephemeral=True, delete_after=10)


async def setup(bot):
    await bot.add_cog(Translate(bot))
