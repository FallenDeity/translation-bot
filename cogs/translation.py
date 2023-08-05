import asyncio
import datetime
import gc
import os
import random
import re
import traceback
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

from cogs.admin import Admin
from cogs.library import Library
from core.bot import Raizel
from core.views.linkview import LinkView
from languages.terms import terms
from utils.handler import FileHandler
from utils.hints import Hints
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
        return await ctx.send(f"> **🚄`{self.bot.translator[ctx.author.id]}`**")

    @commands.hybrid_command(
        help="Send file to be translated with the command. use correct novelname, otherwise you  will be banned",
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
            term: str = None,
            ignore_warnings: bool = False
    ):
        """Check the leaderboard of a user
               Parameters
               ----------
               ctx : commands.Context
                   The interaction
               link :
                   link of file, discord message link, attachment link, temp.sh, mega , etc...
               file :
                    attach a file
               messageid :
                    discord message id.. bot has to have access to that msg link else use discord attachment url
               language :
                    language to which novel to be translated, default english
               novelname :
                    change the novel name to this. if you got not valid name add ongoing with correct novelname here
               rawname :
                    add the raw name of the novel. it will be automatically translated to eng and added in novelname
               library_id :
                    translate the novel from library with this id
               term :
                    add the terms available in bot.. currently we only have chinese terms
               ignore_warnings :
                    give true to ignore the library check
               """
        try:
            await ctx.defer()
        except:
            pass
        name = None
        if link is not None and link.startswith("#"):
            try:
                novel_id = int(link.replace("#", ""))
                library_id = novel_id
            except:
                return await ctx.reply("send a valid id")
        if library_id is not None:
            try:
                novel_data = await self.bot.mongo.library.get_novel_by_id(library_id)
                name = novel_data["title"]
                link = novel_data["download"]
            except:
                return await ctx.reply("send a valid id")
        if self.bot.app_status == "restart":
            return await ctx.reply(
                f"> Bot is scheduled to restart within 60 sec or after all current tasks are completed.. Please try after bot is restarted")
        if ctx.author.id == 925597069748621353:
            while len(asyncio.all_tasks()) >= 9 or (
                    ctx.author.id in self.bot.translator and not self.bot.translator[ctx.author.id] == "waiting"):
                if ctx.author.id not in self.bot.translator:
                    self.bot.translator[ctx.author.id] = f"waiting"
                await asyncio.sleep(20)
                if self.bot.translator[ctx.author.id] == "waiting" and len(self.bot.translator) <= 1:
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
        language = await FileHandler.get_language(language)
        if ctx.author.id in self.bot.translator and not ctx.author.id == 925597069748621353:
            return await ctx.send("> **❌You cannot translate two novels at a time.**", ephemeral=True)
        if not ctx.message.attachments and not file and messageid is None:
            return await ctx.send("> **❌You must add a novel/link to translate**", ephemeral=True)
        msg = None
        novel = None
        file_type = None
        rep_msg = await ctx.reply("Please wait.. Translation will began soon")
        no_tries = 0
        while (len(self.bot.crawler)+len(self.bot.translator)) > 2 or len(self.bot.translator) >= 2:
            no_tries = no_tries + 3
            try:
                rep_msg = await rep_msg.edit(
                    content=f"> **Currently bot is busy.Please wait some time. Please wait till bot become free. will retry automatically in 20sec  ** {str(no_tries)} try")
            except:
                pass
            if no_tries >= 7:
                return await ctx.reply(content="> Currently bot is busy.. please try after some time")
            if no_tries >= 5:
                self.bot.translator = {}
                if len(self.bot.translator) < 2:
                    break
                await asyncio.sleep(20)
            await asyncio.sleep(10)
        if link is not None and ("discord.com/channels" in link or link.isnumeric()):
            messageid = link
            link = None
        if ctx.message.attachments and not str(link).startswith("https://cdn.discordapp.com"):
            link = ctx.message.attachments[0].url
        elif messageid is None and ("mega.nz" in link or "mega.co.nz" in link):
            await ctx.send("Mega link found.... downloading from mega", delete_after=10, ephemeral=True)
            info = await self.bot.loop.run_in_executor(None, self.bot.mega.get_public_url_info, link)
            size = int(info.get("size")) / 1000
            # if size >= 30 * 1000:
            #     await rep_msg.delete()
            #     return await ctx.reply(
            #         "> **❌ File size is too big... Please split the file and translate**"
            #     )
            name = info.get("name")
            name = bytes(name, encoding="raw_unicode_escape", errors="ignore").decode()
            file_type = name.split(".")[-1]
            path = await self.bot.loop.run_in_executor(None, self.bot.mega.download_url,
                                                       link, None, f"{ctx.author.id}.{file_type}")
            if "txt" not in file_type and "epub" not in file_type and "pdf" not in file_type:
                os.remove(path)
                await rep_msg.delete()
                return await ctx.send("> **❌Only .txt, .pdf and .epub supported** use txt for best results",
                                      ephemeral=True)
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
                    if "@me/" in messageid:
                        return await ctx.send(
                            "> Bot can't get attachment urls from dm's.. Please use library id or attachment link")
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
            try:
                resp = await self.bot.con.get(link)
            except:
                await ctx.reply("> Check the link provided. We couldn't connect to the link you provided")
            try:
                file_type = await FileHandler.get_headers(resp)
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
            return await ctx.send("> **❌Only .txt , .pdf and .epub supported** Use txt for best results",
                                  ephemeral=True)
        if novelname is not None:
            name = novelname
        name_check = await FileHandler.checkname(name, self.bot)
        if rawname is not None:
            if not name_check:
                try:
                    name = GoogleTranslator(
                        source="auto", target="english"
                    ).translate(rawname).strip()
                    name_check = await FileHandler.checkname(name, self.bot)
                except:
                    pass
        if (not name_check) and library_id is not None:
            name = await self.bot.mongo.library.get_title_by_id(library_id)
            name_check = await FileHandler.checkname(name, self.bot)
        if "_crawl" in name:
            name = name.replace("_crawl", "")
            if len(name) >= 5:
                name_check = True
        if not name_check:
            await rep_msg.delete()
            return await ctx.reply(
                f"> **❌{name} is not a valid novel name. please provide a valid name to filename before translating. "
                f"**\n If you think name is correct, please add **ongoing** or **complete**(depending on novel status)"
                f" at the end of filename(**eg: {name.split('__')[0]}_ongoing**).."
                f"\nyou can also use novelname or rawname tag in slash command.."
                f" make sure novel name is correct , if its found you are using"
                f" wrong name we(bot-admins) may ban you from using bot"
            )
        for tag in ['/', '\\', '<', '>', "'", '"', ':', ";", '?', '|', '*', ';', '!']:
            name = name.replace(tag, '').strip()
        name = name.replace("__", "--").replace('_', ' ').replace("--", "__")
        library: int = None
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
        novel_data = await self.bot.mongo.library.get_novel_by_name(name)
        if novel_data is not None:
            novel_data = list(novel_data)
            ids = []
            lang_check = False
            eng_check = False
            size_check = False
            name_lib_check = False
            size_found = round(os.path.getsize(f"{ctx.author.id}.txt") / (1024 ** 2), 2) + 0.10
            size_found = 1.375 * size_found
            for n in novel_data:
                ids.append(n._id)
                org_name = re.sub("[^A-Za-z0-9]", "", n.title.split('  ')[0]).lower()
                n_name = re.sub("[^A-Za-z0-9]", "", name.split('  ')[0]).lower()
                org_name2 = re.sub("[^A-Za-z0-9]", "", n.title.split('__')[0]).lower()
                n_name2 = re.sub("[^A-Za-z0-9]", "", name.split('__')[0]).lower()
                # print(f"{org_name}-{org_name2}-{n_name2}-{n_name}")
                # print(f"{language}-{n.language}")
                # print(f"{size_found}-{round(n.size / (1024 ** 2), 2)}")
                if (name.split('__')[0].lower() == n.title.split('__')[0].lower()
                    or n.title.split('  ')[0].lower() == name.split('  ')[0].lower()
                    or org_name == name.strip().lower()
                    or org_name2 == n_name2
                    or n_name == org_name
                    or org_name2 == n_name
                    or (len(name) > 22 and n_name in org_name)
                    or (len(name) > 22 and n_name2 in org_name2)) \
                        and language.lower() in str(n.language).lower() \
                        and size_found >= round(n.size / (1024 ** 2), 2):
                    library = n._id
                    print(library)
                if "english" == str(n.language).lower():
                    eng_check = True
                if language == str(n.language).lower():
                    lang_check = True
                    org_str = ''.join(e for e in name.split('__')[0] if e.isalnum())
                    lib_str = ''.join(e for e in str(n.title).split('__')[0] if e.isalnum())
                    if org_str.lower() in lib_str.lower():
                        name_lib_check = True
                        try:
                            lib_size = round(n.size / (1024 ** 2), 2)
                            if size_found <= lib_size <= 2 * size_found:
                                size_check = True
                                # if library is None:
                                #     library = n._id
                        except:
                            pass
            if len(ids) >= 20:
                library = None
            if lang_check:
                ids = ids[:20]
                rep_msg = await rep_msg.edit(content="Novel is already in our library")
                ctx.command = await self.bot.get_command("library search").callback(Library(self.bot), ctx, name,
                                                                                    language, None, None, None, None,
                                                                                    None,
                                                                                    None, None, False, "size", 20)
                if len(ids) < 4 and name_lib_check:
                    await ctx.send("**Please check from above library**", delete_after=20)
                    await asyncio.sleep(5)
                # if name_lib_check and size_check:
                #     await ctx.send("**Please check from above library**")
                #     await asyncio.sleep(10)
                chk_msg = await ctx.send(embed=discord.Embed(
                    description=f"This novel **{name}** is already in our library with ids **{str(ids)}**...use arrow marks  in above  to navigate...\nIf you want to continue translation react with 🇳 within 10 sec\n\n**Note : Some files are in docx format, so file size maybe half the size of txt. and try to minimize translating if its already in library**"))
                await chk_msg.add_reaction('🇾')
                await chk_msg.add_reaction('🇳')

                def check(reaction, user):
                    if ignore_warnings:
                        return True
                    return reaction.message.id == chk_msg.id and (
                            str(reaction.emoji) == '🇾' or str(reaction.emoji) == '🇳') and user == ctx.author

                try:
                    if ignore_warnings is True:
                        timeout = 1.0
                    else:
                        timeout = 20.0
                    res = await self.bot.wait_for(
                        "reaction_add",
                        check=check,
                        timeout=timeout,
                    )
                except asyncio.TimeoutError:
                    await chk_msg.delete()
                    if ignore_warnings is False:
                        try:
                            os.remove(f"{ctx.author.id}.txt")
                        except:
                            pass
                        await ctx.send("No response detected. ", delete_after=5)
                        return None
                else:
                    if str(res[0]) == '🇳' or ignore_warnings is True:
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
                1054014022019715092
            ) or await self.bot.fetch_channel(1054014022019715092)
            msg_new_id = new_ch.last_message_id
            try:
                msg_new = await new_ch.fetch_message(msg_new_id)
            except:
                msg_new = await new_ch.fetch_message(1069535943738019840)
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
        # if (size := os.path.getsize(f"{ctx.author.id}.txt")) > 25 * 10 ** 6:
        #     os.remove(f"{ctx.author.id}.txt")
        #     return await ctx.reply("The provided file is bigger than 25mb. Please split the file and translate")
        urls = await FileHandler.find_urls_from_text(novel[:1000])
        try:
            novel_url = urls[0]
        except:
            novel_url = None
        # print(f"urls : {urls}")
        size = os.path.getsize(f"{ctx.author.id}.txt")
        scraper = cloudscraper.create_scraper()
        if term:
            term_dict = terms(term)
            if term_dict == {}:
                return await ctx.reply(
                    f"**Please try again with the validterms to be applied :\n\t"
                    f"1 : Naruto \n\t2 : One-Piece \n\t3 : Pokemon\n\t4 : Mixed anime terms\n\t"
                    f"5 : Prince of Tennis\n\t6 : Anime + Marvel + DC\n\t7 : Cultivation terms\n\t"
                )
            novel = term_raw(novel, term_dict)
            await ctx.reply(content=f"> Added terms {term}")
        try:
            thumbnail = ""
            temp = []
            for url in urls:
                try:
                    if "discord.gg" in url:
                        continue
                        # urls.remove(url)
                    response = await self.bot.loop.run_in_executor(None, scraper.get, url)
                    soup = BeautifulSoup(response.text, "lxml")
                    # print(f"url  {url}")
                    thumbnail: str = await FileHandler().get_thumbnail(soup=soup, link=url)
                    # print(f"thub {thumbnail}")
                    if thumbnail is not None and thumbnail.strip() != "":
                        if scraper.get(thumbnail).status_code == 200:
                            # print("break")
                            novel_url = url
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
        # input(f"if {library}")
        try:
            if urls is None or urls == []:
                desc_link = ""
            else:
                desc_link = urls[0]
            try:
                original_Language = await FileHandler.find_language(novel)
            except:
                original_Language = 'NA'
            os.remove(f"{ctx.author.id}.txt")
            try:
                if thumbnail is not None and thumbnail.strip() != "":
                    avatar = thumbnail
                else:
                    avatar = await Hints.get_avatar()
                des = GoogleTranslator().translate(
                    await FileHandler.get_desc_from_text(novel[:5000], title=name, link=desc_link)).strip()
                description = des
            except:
                description = ""
                des = novel[:400]
            embed = discord.Embed(title=str(f"{name[:240]}"), description=f"```yaml\n{des[:350]}```",
                                  colour=discord.Colour.blurple())
            embed.set_thumbnail(url=avatar)
            embed.add_field(name="Translating to", value=language, inline=True)
            embed.add_field(name="From", value=original_Language, inline=True)
            embed.add_field(name="Size", value=f"{round(size / (1024 ** 2), 2)} MB", inline=True)
            embed.set_footer(text=f"Hint : {await Hints.get_single_hint()}", icon_url=await Hints.get_avatar())
            rep_msg = await rep_msg.edit(content="", embed=embed)
            if library is not None:
                await ctx.reply(content=f"> Updating {str(library)} with name : {name}")
            poke_words = ["elves ", "pokemon", "pokémon", " elf "]
            if any(word in name.lower() for word in poke_words):
                term_dict = terms("pokemon")
                novel = term_raw(novel, term_dict)
                await ctx.send("Added pokemon terms", delete_after=5)
            liz = [novel[i: i + 1800] for i in range(0, len(novel), 1800)]
            insert = random.randint(1, 20)
            while True:
                if insert < len(liz) - 3:
                    liz.insert(insert,
                               f" (for more novels ({random.randint(1000, 200000)})join: https://discord.gg/SZxTKASsHq)  ")
                else:
                    break
                insert += random.randint(100, 250)
            liz.append(f"\n\n for more novels ({random.randint(1000, 200000)})join: https://discord.gg/SZxTKASsHq\n")
            self.bot.translator[ctx.author.id] = f"0/{len(liz)}"
            await FileHandler.update_status(self.bot)
            if ctx.author.id != 925597069748621353:
                task = asyncio.create_task(self.cc_prog(rep_msg, embed=embed, author_id=ctx.author.id))
            translate = Translator(self.bot, ctx.author.id, language)
            if len(liz) < 1700:
                story = await translate.start(liz, len(asyncio.all_tasks()))
            else:
                if ctx.author.id == 925597069748621353:
                    await asyncio.sleep(30)
                chunks = [liz[x:x + 1000] for x in range(0, len(liz), 1000)]
                del liz
                filename = f"{str(random.randint(1000, 10000))}.txt"
                await ctx.reply(content=f"> Found large file... bot  will split it into  chunks  and translate  the  "
                                        f"file  and merge it automatically... so  progress wouldn't work correctly. "
                                        f"Please be patient")
                cnt = 0
                attachment_links: list[str] = []
                tr_channel = await self.bot.fetch_channel(1054014022019715092)
                for liz_t in chunks:
                    cnt += 1
                    print(len(liz_t))
                    self.bot.translator[ctx.author.id] = f"0/{len(liz_t)}"
                    translate = Translator(self.bot, ctx.author.id, language)
                    try:
                        pr_msg = await ctx.reply(
                            content=f"> Translating {str(cnt)} chunks out of {str(len(chunks))}... use .tp to "
                                    f"check progress")
                    except:
                        pass
                    story = await translate.start(liz_t, len(asyncio.all_tasks()) + 2)
                    async with aiofiles.open(filename, "w", encoding="utf-8", errors="ignore") as f:
                        await f.write(story)
                    atm_msg = await tr_channel.send(file=discord.File(f"{filename}", f"{name}_part{cnt}.txt"))
                    os.remove(filename)
                    attachment_links.append(atm_msg.attachments[0].url)
                    del translate
                    del story
                    gc.collect()
                    try:
                        await pr_msg.delete()
                        del liz_t
                        gc.collect()
                        chunks[cnt - 1] = []
                    except:
                        pass
                await ctx.reply(content=f"Translated {str(len(chunks))} chunks")
                for at_link in attachment_links:
                    resp = await self.bot.con.get(at_link)
                    data = await resp.read()
                    async with aiofiles.open(filename, "a+", encoding="utf-8", errors="ignore") as f:
                        await f.write(data.decode(encoding="utf-8", errors="ignore"))
                try:
                    async with aiofiles.open(filename, "r", encoding="utf-8", errors="ignore") as f:
                        story = await f.read()
                    os.remove(filename)
                    del chunks
                except:
                    pass
            try:
                task.cancel()
                embed.set_field_at(index=3,
                                   name=f"Progress :  100%",
                                   value=progressBar.filledBar(100, 100,
                                                               size=10, line="🟥", slider="🟩")[
                                       0])
                await rep_msg.edit(embed=embed)
            except:
                pass
            async with aiofiles.open(f"{ctx.author.id}.txt", "w", encoding="utf-8", errors="ignore") as f:
                await f.write(story)
            if description.strip() == "":
                try:
                    description = GoogleTranslator(source="auto", target="english").translate(
                        await FileHandler.get_desc_from_text(story[:10000], title=name)).strip()
                except:
                    description = await FileHandler.get_desc_from_text(story[:10000], title=name)
            return await FileHandler().distribute(self.bot, ctx, name, language, original_Language, rawname,
                                                  description,
                                                  thumbnail=thumbnail, library=library, novel_url=novel_url)
        except Exception as e:
            if "Translation stopped" in str(e):
                return await ctx.send("Translation stopped")
            else:
                print(e)
                traceback.print_exc()
                raise e
        finally:
            await FileHandler.update_status(self.bot)
            try:
                del story
                del novel
                del liz
                if len(asyncio.all_tasks()) < 8:
                    asyncio.create_task(self.bot.load_title())
            except:
                pass
            try:
                del self.bot.translator[ctx.author.id]
            except:
                pass
            try:
                if (self.bot.translation_count >= 20 or self.bot.crawler_count >= 25) and self.bot.app_status == "up":
                    await ctx.reply(
                        "> **Bot will be Restarted when the bot is free due to max limit is reached.. Please be patient")
                    chan = self.bot.get_channel(
                        991911644831678484
                    ) or await self.bot.fetch_channel(991911644831678484)
                    msg_new2 = await chan.fetch_message(1052750970557308988)
                    context_new2 = await self.bot.get_context(msg_new2)
                    asyncio.create_task(
                        self.bot.get_command("restart").callback(Admin(self.bot), context_new2))

            except:
                pass
            try:
                await FileHandler.update_status(self.bot)
                gc.collect()
                return
            except:
                print("error in garbage collection")

    @translate.autocomplete("language")
    async def translate_complete(
            self, inter: discord.Interaction, language: str
    ) -> list[app_commands.Choice]:
        lst = [i for i in self.bot.all_langs if language.lower() in i.lower()][:25]
        return [app_commands.Choice(name=i, value=i) for i in lst]

    async def cc_prog(self, msg: discord.Message, embed: discord.Embed, author_id: int) -> typing.Optional[
        discord.Message]:
        bardata = progressBar.filledBar(100, 0, size=10, line="🟥", slider="🟩")
        embed.add_field(name="Progress", value=f"{bardata[0]}", inline=False)
        while author_id in self.bot.translator:
            out = self.bot.translator[author_id]
            split = out.split("/")
            if split[0].isnumeric():
                embed.set_field_at(index=3,
                                   name=f"Progress :  {str(round(eval(out) * 100, 2))}%  ({out})",
                                   value=progressBar.filledBar(int(split[1]), int(split[0]),
                                                               size=10, line="🟥", slider="🟩")[
                                             0] + f"  {discord.utils.format_dt(datetime.datetime.now(), style='R')}")
                await msg.edit(embed=embed)
            else:
                break
            if len(asyncio.all_tasks()) >= 9:
                embed.set_field_at(index=3,
                                   name=f"Progress : ",
                                   value=f"progress bar is closed .please use .tp to check progress")
                return await msg.edit(embed=embed)
            await asyncio.sleep(8)

        embed.set_field_at(index=3,
                           name=f"Progress :  100%",
                           value=progressBar.filledBar(100, 100,
                                                       size=10, line="🟥", slider="🟩")[
                               0])
        # print(embed)
        return await msg.edit(embed=embed)

    @commands.hybrid_command(
        help="translate multiple files together one at a time"
    )
    async def multi(self, ctx: commands.Context, language: str = "english", add_terms: str = None, messageid: str = None, ):
        """Translate multiple text files
               Parameters
               ----------
               ctx : commands.Context
                   The interaction
               language :
                   language to translate to, by default english
               messageid :
                    message id of the attachments, bot has to have access to this message
               add_terms:
                    add terms to novel added before translating. currently we only have chinese terms
               """
        try:
            await ctx.defer()
        except:
            pass
        if language is not None and ("discord.com/channels" in language or language.isnumeric()):
            messageid = language
            language = "english"
        if messageid:
            if 'discord' in messageid:
                spl_link = messageid.split('/')
                server_id = int(spl_link[4])
                channel_id = int(spl_link[5])
                messageid = int(spl_link[6])
                server = self.bot.get_guild(server_id)
                channel = server.get_channel(channel_id)
            else:
                if messageid.isnumeric():
                    messageid = int(messageid)
                else:
                    return ctx.reply(content=">Invalid message id")
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
        language = await FileHandler.get_language(language)
        if not message.attachments:
            return await ctx.reply(content="> Attach a file to translate")
        count = 1
        for attached in message.attachments:
            if count < len(message.attachments):
                self.bot.app_status = "multi"
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
                ctx.command = await self.bot.get_command("translate").callback(Translate(self.bot), ctx_new,
                                                                               attached.url,
                                                                               None,
                                                                               None,
                                                                               language, None, None,
                                                                               None,
                                                                               add_terms, True)
                await asyncio.sleep(5)
                self.bot.app_status = "up"

            except Exception as e:
                if "TooManyRequests" in str(e):
                    raise e
                else:
                    print(e)
                    ctx_new = self.bot.get_context(message)
                    self.bot.app_status = "up"
                    return await ctx_new.send(f"> Error occurred in translating {attached.filename}\ndue to : {str(e)}")
            finally:
                self.bot.app_status = "up"
        return

    @multi.autocomplete("language")
    async def translate_complete(
            self, inter: discord.Interaction, language: str
    ) -> list[app_commands.Choice]:
        lst = [i for i in self.bot.all_langs if language.lower() in i.lower()][:25]
        return [app_commands.Choice(name=i, value=i) for i in lst]

    @multi.autocomplete("add_terms")
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

    @translate.autocomplete("term")
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
