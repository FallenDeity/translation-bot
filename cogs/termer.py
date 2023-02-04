import asyncio
import gc
import os
import random
import typing
from urllib.parse import urljoin

import aiofiles
import cloudscraper
import discord
from StringProgressBar import progressBar
from bs4 import BeautifulSoup
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
        try:
            await ctx.defer()
        except:
            pass
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
        # if self.bot.app_status == "restart":
        #     return await ctx.reply(
        #         f"> Bot is scheduled to restart within 60 sec or after all current tasks are completed.. Please try after bot is restarted")
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
        if ctx.author.id in self.bot.translator and not ctx.author.id == 925597069748621353:
            return await ctx.send("> **❌You cannot translate two novels at a time.**")
        if not ctx.message.attachments and not file and messageid is None:
            return await ctx.send("> **❌You must add a novel/link to translate**")
        msg = None
        novel = None
        file_type = None
        name = None
        rep_msg = await ctx.reply("Please wait.. Translation will began soon")
        no_tries = 0
        while len(asyncio.all_tasks()) >= 9 or len(self.bot.translator) >= 3:
            no_tries = no_tries + 1
            rep_msg = await rep_msg.edit(
                content=f"> **Currently bot is busy.Please wait some time. Please wait till bot become free. will retry automatically in 20sec  ** {str(no_tries)} try")
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
            await ctx.send("Mega link found.... downloading from mega", delete_after=5)
            info = await self.bot.loop.run_in_executor(None, self.bot.mega.get_public_url_info, link)
            size = int(info.get("size")) / 1000
            if size >= 30 * 1000:
                await rep_msg.delete()
                return await ctx.reply(
                    "> **❌ File size is too big... Please split the file and translate"
                )
            name = info.get("name")
            name = bytes(name, encoding="raw_unicode_escape", errors="ignore").decode()
            file_type = name.split(".")[-1]
            path = await self.bot.loop.run_in_executor(None, self.bot.mega.download_url,
                                                       link, None, f"{ctx.author.id}.{file_type}")
            file_type = path.suffix.replace(".", "")
            name = name.replace(".txt", "").replace(".docx", "").replace(".epub", "").replace(".pdf", "")
            if "txt" not in file_type and "epub" not in file_type:
                os.remove(path)
                await rep_msg.delete()
                return await ctx.send("> **❌Only .txt, .pdf and .epub supported**")
            name = name[:100]
            # os.rename(path, f"{ctx.author.id}.{file_type}")
            # if "docx" in file_type:
            #     await FileHandler.docx_to_txt(ctx, file_type)
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
        # elif "document" in file_type.lower() or "docx" in file_type.lower():
        #     file_type = "docx"
        elif "epub" in file_type.lower():
            file_type = "epub"
        elif "pdf" in file_type.lower():
            file_type = "pdf"
        else:
            return await ctx.send("> **❌Only .txt, .pdf and .epub supported**Use txt for best results")
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
        if (not name_check) and library_id is not None:
            name = await self.bot.mongo.library.get_title_by_id(library_id)
            name_check = FileHandler.checkname(name, self.bot)
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
            eng_check = False
            size_check = False
            name_lib_check = False
            for n in novel_data:
                ids.append(n._id)
                if "english" == n.language:
                    eng_check = True
                if language == n.language:
                    lang_check = True
                if name in n.title:
                    name_lib_check = True
                try:
                    size_found = round(os.path.getsize(f"{ctx.author.id}.txt") / (1024 ** 2), 2) - 0.01
                    lib_size = round(n.size / (1024 ** 2), 2)
                    if size_found <= lib_size:
                        size_check = True
                except:
                    pass
            if lang_check:
                ids = ids[:20]
                ctx.command = await self.bot.get_command("library search").callback(Library(self.bot), ctx, name,
                                                                                    language, None, None, None, None, None,
                                                                                    None, None, False, "size", 20)
                if len(ids) < 5 or name_lib_check:
                    await ctx.send("**Please check from above library**", delete_after=20)
                    await asyncio.sleep(12)
                if name_lib_check and size_check:
                    await ctx.send("**Please check from above library**")
                    return None
                chk_msg = await ctx.send(embed=discord.Embed(
                    description=f"**This novel is already in our library... **\n If you want to continue translation react with 🇳"))
                await chk_msg.add_reaction('🇾')
                await chk_msg.add_reaction('🇳')

                def check(reaction, user):
                    return reaction.message.id == chk_msg.id and (
                            str(reaction.emoji) == '🇾' or str(reaction.emoji) == '🇳') and user == ctx.author

                try:
                    res = await self.bot.wait_for(
                        "reaction_add",
                        check=check,
                        timeout=16.0,
                    )
                except asyncio.TimeoutError:
                    print('error')
                    try:
                        os.remove(f"{ctx.author.id}.txt")
                    except:
                        pass
                    await ctx.send("No response detected. ", delete_after=10)
                    await chk_msg.delete()
                    return None
                else:
                    await ctx.send("Reaction received", delete_after=10)

                    if str(res[0]) == '🇳':
                        await chk_msg.delete()
                    else:
                        try:
                            os.remove(f"{ctx.author.id}.txt")
                        except:
                            pass
                        await chk_msg.delete()
                        return None
        if (novel_data is None or not eng_check) and not language.lower() == "english":
            new_ch = self.bot.get_channel(
                1054014022019715092
            ) or await self.bot.fetch_channel(1054014022019715092)
            msg_new_id = new_ch.last_message_id
            msg_new = await new_ch.fetch_message(msg_new_id)
            context_new = await self.bot.get_context(msg_new)
            try:
                asyncio.create_task(
                    self.bot.get_command("translate").callback(Termer(self.bot), context_new, term, link,
                                                               file,
                                                               None,
                                                               "english", novelname, rawname, library_id))
            except:
                pass
        if novel is None:
            data = await resp.read()
            async with aiofiles.open(f"{ctx.author.id}.{file_type}", "wb") as f:
                await f.write(data)
            # if "docx" in file_type:
            #     await FileHandler.docx_to_txt(ctx, file_type)
            if "epub" in file_type:
                await FileHandler.epub_to_txt(ctx)
            if "pdf" in file_type:
                await FileHandler.pdf_to_txt(ctx)
            novel = await FileHandler().read_file(ctx)
        if (size := os.path.getsize(f"{ctx.author.id}.txt")) > 30 * 10 ** 6:
            os.remove(f"{ctx.author.id}.txt")
            return await ctx.reply("The provided file is bigger than 20mb. Please split the file and translate")
        rep_msg = await rep_msg.edit(content=f"> **✅Terming started. **")
        novel = self.term_raw(novel, term_dict)
        msg_content = f"> **✅Terming completed.. Started Translating 📔{name} Translating to {language}.**"
        rep_msg = await rep_msg.edit(
            content=msg_content
        )
        urls = FileHandler.find_urls_from_text(novel[:3000])
        scraper = cloudscraper.create_scraper()
        try:
            thumbnail = ""
            temp = []
            for url in urls:
                try:
                    response = scraper.get(url, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
                    })
                    soup = BeautifulSoup(response.text, "lxml")
                    # print(f"url  {url}")
                    thumbnail: str = await FileHandler().get_thumbnail(soup=soup, link=url)
                    print(f"thub {thumbnail}")
                    if thumbnail is not None and thumbnail.strip() != "":
                        if scraper.get(thumbnail).status_code == 200:
                            print("break")
                            break
                        else:
                            # print("else")
                            thumbnail = ""
                    if thumbnail == "":
                        try:
                            for img in soup.find_all('img'):
                                img_url = urljoin(url, img.get('src'))
                                if scraper.get(img_url).status_code == 200:
                                    if "jpg" in img_url.lower() or "jpeg" in img_url.lower():
                                        temp.insert(0, img_url)
                                    else:
                                        temp.append(img_url)
                        except:
                            pass
                except Exception as e:
                    print(e)
            if urls != [] and temp != [] and thumbnail == "":
                thumbnail = random.choice(temp[0:3])

        except:
            thumbnail = ""
        # print(f"thumbnail {thumbnail}")
        try:
            os.remove(f"{ctx.author.id}.txt")
            original_Language = FileHandler.find_language(novel)
            try:
                if thumbnail is not None and thumbnail.strip() != "":
                    avatar = thumbnail
                else:
                    avatar = ctx.author.display_avatar
                des = GoogleTranslator().translate(
                    await FileHandler.get_desc_from_text(novel[:5000], title=name)).strip()
                description = des
            except:
                description = ""
                des = novel[:400]
            embed = discord.Embed(title=str(f"{name[:240]}"), description=des[:350],
                                  colour=discord.Colour.blurple())
            embed.set_thumbnail(url=avatar)
            embed.add_field(name="Translating to", value=language, inline=True)
            embed.add_field(name="From", value=original_Language, inline=True)
            embed.add_field(name="Size", value=f"{round(size / (1024 ** 2), 2)} MB", inline=False)
            rep_msg = await rep_msg.edit(content="", embed=embed)
            liz = [novel[i: i + 1800] for i in range(0, len(novel), 1800)]
            self.bot.translator[ctx.author.id] = f"0/{len(liz)}"
            asyncio.create_task(self.cc_prog(rep_msg, embed, ctx.author.id))
            translate = Translator(self.bot, ctx.author.id, language)
            story = await translate.start(liz, len(asyncio.all_tasks()))
            async with aiofiles.open(f"{ctx.author.id}.txt", "w", encoding="utf-8") as f:
                await f.write(story)
            if description.strip() == "":
                try:
                    description = GoogleTranslator(source="auto", target="english").translate(
                        await FileHandler.get_desc_from_text(story[:5000])).strip()
                except:
                    description = await FileHandler.get_desc_from_text(story[:10000])
            await FileHandler().distribute(self.bot, ctx, name, language, original_Language,
                                           raw_name=rawname, description=description)
        except Exception as e:
            if "Translation stopped" in str(e):
                return await ctx.send("Translation stopped")
            else:
                raise Exception
        finally:
            try:
                del story
                del novel
                del liz
            except:
                pass
            try:
                del self.bot.translator[ctx.author.id]
                self.bot.titles.append(name)
            except:
                pass
            try:
                gc.collect()
            except:
                print("error in garbage collection")

    @termer.autocomplete("language")
    async def translate_complete(
            self, inter: discord.Interaction, language: str
    ) -> list[app_commands.Choice]:
        lst = [i for i in self.bot.all_langs if language.lower() in i.lower()][:25]
        return [app_commands.Choice(name=i, value=i) for i in lst]

    async def cc_prog(self, msg: discord.Message, embed: discord.Embed, author_id: int) -> typing.Optional[
        discord.Message]:
        bardata = progressBar.filledBar(100, 0, size=10, line="🟥", slider="🟩")
        embed.add_field(name="Progress", value=f"{bardata[0]}", inline=False)
        value = 0
        while author_id in self.bot.translator:
            out = self.bot.translator[author_id]
            split = out.split("/")
            if split[0].isnumeric() and value <= eval(out):
                embed.set_field_at(index=3,
                                   name=f"Progress :  {str(round(eval(out) * 100, 2))}%",
                                   value=progressBar.filledBar(int(split[1]), int(split[0]),
                                                               size=10, line="🟥", slider="🟩")[
                                       0])
                # print(embed)
                await msg.edit(embed=embed)
                value = eval(out)
            else:
                break
            await asyncio.sleep(8)

        embed.set_field_at(index=3,
                           name=f"Progress :  100%",
                           value=progressBar.filledBar(100, 100,
                                                       size=10, line="🟥", slider="🟩")[
                               0])
        # print(embed)
        return await msg.edit(embed=embed)

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
