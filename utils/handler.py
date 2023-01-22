import asyncio
import datetime
import os
import random
import re
import typing
from urllib.parse import urljoin
from collections import OrderedDict

import PyPDF2
import aiofiles
import chardet
import cloudscraper
import discord
# import docx
import ebooklib
import parsel
from PyDictionary import PyDictionary
from deep_translator import single_detection
from discord.ext import commands
from ebooklib import epub
from readabilipy import simple_json_from_html_string
from textblob import TextBlob
from bs4 import BeautifulSoup

from core.bot import Raizel
from core.views.linkview import LinkView
from databases.data import Novel
from databases.mongo import get_regex_from_name
from languages import languages
from utils.category import Categories


def chapter_to_str(chapter):
    sel = parsel.Selector(str(chapter.get_content().decode()))
    text = sel.css("* ::text").extract()
    return "\n".join(text)


class FileHandler:
    ENCODING: list[str] = ["utf-8", "cp936", "utf-16", "cp949"]
    TOTAL: int = len(ENCODING)

    @staticmethod
    def find_urls_from_text(string):
        # findall() has been used
        # with valid conditions for urls in string
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        url = re.findall(regex, string)
        return [x[0] for x in url]

    @staticmethod
    async def get_desc_from_text(text: str, title: str = None):
        desc = ["introduction", "description", "简介", "描述", "描写", "summary", "prologue", "概括", "摘要", "总结", "序幕", "开场白"]
        text = '\n'.join(OrderedDict.fromkeys(text.split('\n')))# remove  duplicate lines from description
        if title:
            text = re.sub(re.compile(get_regex_from_name(title), flags=re.IGNORECASE), "", text) #remove title from description
        for d in desc:
            if d in text.lower():
                description = re.split(d, text, flags=re.IGNORECASE)[1][:500].replace(":", "").replace("\n\n",
                                                                                                       "").strip()
                description = re.sub(r'(\n\s*)+\n', '\n', description)
                return description
        return re.sub(r'(\n\s*)+\n', '\n', text[:500].strip())

    @staticmethod
    async def get_description(soup: "BeautifulSoup", link: str = "empty", next: str = None, title: str = None) -> str:
        aliases = ("description", "Description", "DESCRIPTION", "desc", "Desc", "DESC")
        description = ""
        if next:
            scraper = cloudscraper.CloudScraper()
            response = scraper.get(link)
            response.encoding = response.apparent_encoding
            article = simple_json_from_html_string(response.text)
            text = ""
            temp = article['plain_text']
            for i in temp:
                text += i['text'] + "\n"
            if title:
                text = text.replace(title, "")
            description = await FileHandler.get_desc_from_text(text, title)
            if description is not None and description.strip() != "":
                return description
        if "69shu" in link:
            scraper = cloudscraper.CloudScraper()  # CloudScraper inherits from requests.Session
            href = urljoin(link, parsel.Selector(scraper.get(link).text).css("div.titxt ::attr(href)").extract_first())
            response = scraper.get(href)
            response.encoding = response.apparent_encoding
            description = "\n".join(parsel.Selector(response.text).css("div.navtxt ::text").extract())
            description = await FileHandler.get_desc_from_text(description, title)
            if description is not None and description.strip() != "":
                return description
        for meta in soup.find_all("meta"):
            if meta.get("name") in aliases:
                description += meta.get("content")
        if description is None:
            description = ""
        return description

    @staticmethod
    def get_tags(text: str) -> list[str]:
        text = text.replace("_", " ")
        text = TextBlob(text)
        return list(set(text.noun_phrases))

    @staticmethod
    def get_language(lang_code: str) -> str:
        lang = languages.choices
        if lang_code in lang:
            language = {lang_code}
        else:
            language = {i for i in lang if lang[i] == lang_code}
        return language.pop()

    @staticmethod
    def find_language(text: str, link: str = None) -> str:
        if link is not None:
            for l in ["bixiange", "trxs", "txt520", "powanjuan", "tongrenquan", "jpxs", "ptwxz", "qidian",
                      "xindingdian", "longteng", "akshu8", "qbtr"]:
                if l in link:
                    return 'chinese (simplified)'
        api_keys = ['8ca7a29f3b7c8ac85487451129f35c89', '1c2d644450cb8923818607150e7766d4',
                    '5cd7b28759bb7aafe9b1d395824e7a67', 'af207e865e0277f375348293a30bcc5e']
        try:
            if "title_name " in text:
                text = text.replace("title_name ", "")
                lang_code = single_detection(str(text[:120]), api_key=random.choice(api_keys))
            else:
                lang_code = single_detection(text[200:250].__str__(), api_key=random.choice(api_keys))
        except:
            try:
                lang_code = single_detection(text[1:100].__str__(), api_key=random.choice(api_keys))
            except:
                lang_code = 'NA'
        if lang_code == 'zh':
            original_Language = ['chinese (simplified)']
        elif lang_code == 'NA':
            original_Language = ['NA']
        else:
            lang = languages.choices
            original_Language = {i for i in lang if lang[i] == lang_code}
        if original_Language == set() or original_Language == [set()]:
            original_Language = FileHandler.find_language(text[600:700])

        try:
            original_Language = original_Language.pop()
        except:
            try:
                original_Language = original_Language.replace("['", "").replace("']", "")
            except:
                pass
        return original_Language

    @staticmethod
    def checkname(name: str, bot: Raizel):
        name = name.replace("-", "_")
        name = name.replace(" ", "_")
        name = name.replace("%20", "_")
        name = name.replace("Chapter", "")
        name = name.replace("chapter", "")
        spl = name.split("_")
        dictionary = PyDictionary()
        segment = 0
        if len(spl) == 1:
            return False
        for t in spl:
            if t is None or t == "":
                continue
            if not t[-1].isalpha():
                t = t[:-1]
            if (
                    t[:-1].isalpha()
                    and len(t) > 3
                    and (bool(dictionary.meaning(str(t), disable_errors=True)) or t.lower() in bot.dictionary)
            ):
                if len(t) > 5 or segment == 2:
                    return True
                else:
                    segment += 1
        return False

    @staticmethod
    async def find_toc_next(soup: BeautifulSoup, link: str = None):
        selectors = ("下一页", "next page", ">", "next") #下一页  "下一章"- next chp 下一页
        for a in soup.find_all("a"):
            # print(a.get('href'))
            if any(selector == a.get_text().lower() for selector in selectors):
                # print("toc true")
                return urljoin(link, a.get('href'))
        print("tocfalse")
        return None

    @staticmethod
    async def find_next_chps(soup: BeautifulSoup, link: str = None):
        selectors = ("下一页", "next page", "下一章", "next chapter", "next")  # 下一页  "下一章"- next chp 下一页
        for a in soup.find_all("a"):
            # print(a.get('href'))
            if any(selector == a.get_text().lower() for selector in selectors):
                # print("next true")
                return urljoin(link, a.get('href'))
        return None

    # @staticmethod
    # async def docx_to_txt(ctx: commands.Context, file_type: str):
    #     msg = await ctx.reply(
    #         "> **✔Docx file detected please wait while we finish converting.**"
    #     )
    #     try:
    #         doc = docx.Document(f"{ctx.author.id}.{file_type}")
    #         string = "\n".join([para.text for para in doc.paragraphs])
    #         async with aiofiles.open(f"{ctx.author.id}.txt", "w", encoding="utf-8") as f:
    #             await f.write(string)
    #         await msg.delete()
    #         os.remove(f"{ctx.author.id}.docx")
    #     except Exception as e:
    #         await ctx.send("error occured in converting docx to txt")

    @staticmethod
    async def epub_to_txt(ctx: commands.Context):
        msg = await ctx.reply("> **Epub file detected please wait till we finish converting to .txt")
        book = epub.read_epub(f"{ctx.author.id}.epub")
        items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
        text = ""
        for i in items:
            try:
                text += chapter_to_str(i) + "\n\n---------------------xxx---------------------\n\n"
            except:
                pass
        with open(f"{ctx.author.id}.txt", "w", encoding="utf-8") as f:
            f.write(text)
        await msg.delete()
        os.remove(f"{ctx.author.id}.epub")

    @staticmethod
    async def pdf_to_txt(ctx: commands.Context):
        msg = await ctx.reply("> **PDF file detected. converting to txt")
        with open(f'{ctx.author.id}.pdf', 'rb') as pdfFileObj:
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            full_text = ""
            for i in range(0, pdfReader.numPages):
                pageObj = pdfReader.getPage(i)
                full_text += pageObj.extractText()
        await msg.delete()
        with open(f"{ctx.author.id}.txt", "w", encoding="utf-8") as f:
            f.write(full_text)
        os.remove(f"{ctx.author.id}.pdf")

    async def read_file(
            self, ctx: commands.Context
    ) -> typing.Union[str, discord.Message]:
        novel = None
        for i, j in enumerate(self.ENCODING):
            try:
                async with aiofiles.open(f"{ctx.author.id}.txt", "r", encoding=j) as f:
                    novel = await f.read()
                    break
            except (UnicodeDecodeError, UnicodeError):
                if i == self.TOTAL - 1:
                    try:
                        await ctx.send(
                            "> **✔Encoding not in db trying to auto detect please be patient.**"
                        )
                        async with aiofiles.open(f"{ctx.author.id}.txt", "rb") as f:
                            novel = await f.read()
                        async with aiofiles.open(
                                f"{ctx.author.id}.txt",
                                "r",
                                encoding=chardet.detect(novel[:500])["encoding"],
                                errors="ignore",
                        ) as f:
                            novel = await f.read()
                    except Exception as e:
                        print(e)
                        return await ctx.reply(
                            "> **❌Currently we are only translating korean and chinese.**"
                        )
        return novel

    @staticmethod
    def get_headers(response) -> str:
        string = "".join(
            [
                i
                for i in response.headers["Content-Disposition"].split(".")[-1]
                if i.isalnum()
            ]
        )
        return string

    @staticmethod
    def tokenize(link: str) -> tuple[str, ...]:
        url = link.replace(".html", "").replace(".htm/", "")
        suffix = url.split("/")[-1]
        midfix = url.replace(f"/{suffix}", "").split("/")[-1]
        prefix = url.replace(f"/{midfix}/{suffix}", "")
        return url, suffix, midfix, prefix

    async def get_thumbnail(self, soup, link) -> str:
        scraper = cloudscraper.create_scraper()
        if "69shu" in link and "txt" not in link:
            link = urljoin(link, parsel.Selector(scraper.get(link).text).css("div.titxt ::attr(href)").extract_first())
            soup = BeautifulSoup(scraper.get(link).text, "html.parser")
        url, suffix, midfix, prefix = FileHandler.tokenize(link)
        compound = (
            "readwn",
            "fannovels",
            "novelmt",
            "wuxiax",
        )
        imgs = []
        meta = soup.find_all("meta")
        tag = "src" if not any(str(i) in link for i in compound) else "data-src"
        for img in soup.find_all("img"):
            if any(x in img.get(tag, "") for x in ("cover", "thumb", ".jpg", "upload")) and ".png" not in img.get(
                    tag, ""
            ):
                imgs.append(img.get(tag, ""))
        if imgs:
            img = imgs[0]
            for i in imgs:
                if (str("novelsknight") in link and "resize=" in i) or (
                        suffix in i or "/file" in i or midfix in i
                ):
                    img = i
                    if "images/logo.png" in img:
                        continue
                    if "http" not in img:
                        img = urljoin(link, img)
                    if img == "https://novelsknight.com/wp-content/uploads/2022/10/knight.jpg" or \
                            "bixiange.me/images/logo.png" in img or "powanjuan.cc/images/logo.png" in img:
                        continue
                    if scraper.get(img).status_code == 200:
                        return img
        meta = soup.find_all("meta")
        for i in meta:
            if i.get("property") == "og:image":
                return urljoin(link, i.get("content", ""))
        for i in meta:
            if i.get("property") == "twitter:image":
                print(i.get("content"))
                return urljoin(link, i.get("content", ""))
        return ""

    async def get_og_image(self, soup: BeautifulSoup, link: str):
        meta = soup.find_all("meta")
        for i in meta:
            if i.get("property") == "og:image":
                print(i.get("content"))
                return urljoin(link, i.get("content", ""))
        for i in meta:
            if i.get("property") == "twitter:image":
                print(i.get("content"))
                return urljoin(link, i.get("content", ""))
        return await FileHandler().get_thumbnail(soup, link)

    async def distribute(
            self, bot: Raizel, ctx: commands.Context, name: str, language: str, original_language: str, raw_name: str,
            description: str = "", thumbnail: str = ""
    ) -> None:
        download_url = None
        next_no = await bot.mongo.library.next_number
        category = "Uncategorised"
        bot.translation_count = bot.translation_count + 1
        if (os.path.getsize(f"{ctx.author.id}.txt")) > 4 * 10 ** 6:
            bot.translation_count = bot.translation_count + 1
        try:
            category = Categories.from_string(name)
            if category == "Uncategorised":
                category = Categories.from_string(description)
            if thumbnail.strip() == "":
                thumbnail = Categories.thumbnail_from_category(category)
        except Exception as e:
            print("exception in  getting category")
            print(e)
            if thumbnail.strip() == "":
                thumbnail = Categories.thumbnail_from_category(category)
        embed = discord.Embed(title=str(f"#{next_no} : " + name[:240]), description=description[:350],
                              colour=discord.Colour.dark_gold())
        embed.add_field(name="Category", value=category)
        embed.add_field(name="Language", value=language)
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f"Uploaded by {ctx.author}", icon_url=ctx.author.display_avatar)
        if (size := os.path.getsize(f"{ctx.author.id}.txt")) > 8 * 10 ** 6:
            bot.translation_count = bot.translation_count + 1
            if (size := os.path.getsize(f"{ctx.author.id}.txt")) > 13 * 10 ** 6:
                bot.translation_count = bot.translation_count + 2
            try:
                await ctx.send(
                    "Translation Completed... Your novel is too big.We are uploading to Mega.. Please wait",
                    delete_after=5,
                )
                os.rename(f"{ctx.author.id}.txt", f"{name}.txt")
                file = bot.mega.upload(f"{name}.txt")
                filelnk = bot.mega.get_upload_link(file)
                view = LinkView({"Novel": [filelnk, "📔"]})
                await ctx.reply(
                    content=f"> **✔{ctx.author.mention} your novel #{next_no} {name} is ready.**",
                    view=view,
                )
                if original_language.lower() == "korean":
                    channel = bot.get_channel(
                        1032638028868501554
                    ) or await bot.fetch_channel(1032638028868501554)
                else:
                    channel = bot.get_channel(
                        1005668482475643050
                    ) or await bot.fetch_channel(1005668482475643050)
                await channel.send(
                    embed=embed, view=view, allowed_mentions=discord.AllowedMentions(users=False)
                )
                download_url = filelnk
            except Exception as e:
                print(e)
                await ctx.reply(
                    "**Sorry your file was too big please split it and try again.**"
                )
            os.remove(f"{name}.txt")
        else:
            file = discord.File(f"{ctx.author.id}.txt", f"{name}.txt")
            await ctx.reply(content=f"**🎉Here is your translated novel #{next_no}**", file=file)
            if original_language.lower() == "korean":
                channel = bot.get_channel(
                    1032638028868501554
                ) or await bot.fetch_channel(1032638028868501554)
            else:
                channel = bot.get_channel(
                    1005668482475643050
                ) or await bot.fetch_channel(1005668482475643050)
            msg = await channel.send(
                embed=embed, file=discord.File(f"{ctx.author.id}.txt", f"{name}.txt"),
                allowed_mentions=discord.AllowedMentions(users=False)
            )
            os.remove(f"{ctx.author.id}.txt")
            try:
                file.close()
            except:
                pass
            download_url = msg.attachments[0].url
        if raw_name is not None:
            name = name + "__" + raw_name
        if download_url and size > 0.3 * 10 ** 6:
            novel_data = [
                await bot.mongo.library.next_number,
                name,
                description,
                0,
                language,
                self.get_tags(name),
                download_url,
                size,
                ctx.author.id,
                datetime.datetime.utcnow().timestamp(),
                thumbnail,
                original_language,
                category
            ]
            data = Novel(*novel_data)
            try:
                await bot.mongo.library.add_novel(data)
            except:
                loop = True
                no_of_tries = 0
                while loop and no_of_tries < 6:
                    print(f"couldn't add to library... trying for {no_of_tries + 2} times")
                    try:
                        await asyncio.sleep(3)
                        data[0] = await bot.mongo.library.next_number
                        await bot.mongo.library.add_novel(data)
                        loop = False
                    except:
                        no_of_tries += 1

    async def crawlnsend(
            self, ctx: commands.Context, bot: Raizel, title: str, title_name: str, originallanguage: str,
            description: str = None, thumbnail: str = ""
    ) -> str:
        download_url = None
        next_no = await bot.mongo.library.next_number
        category = "Uncategorised"
        bot.crawler_count = bot.crawler_count + 1
        if description is None:
            description = ""
        try:
            category = Categories.from_string(title)
            if category == "Uncategorised":
                category = Categories.from_string(description)
            if thumbnail.strip() == "":
                thumbnail = Categories.thumbnail_from_category(category)
        except Exception as e:
            print("exception in  getting category")
            print(e)
            if thumbnail.strip() == "":
                thumbnail = Categories.thumbnail_from_category(category)
        embed = discord.Embed(title=str(f"#{next_no} : " + title[:240]), description=description[:350],
                              colour=discord.Colour.dark_gold())
        embed.add_field(name="Category", value=category)
        embed.add_field(name="Language", value=originallanguage)
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f"Uploaded by {ctx.author}", icon_url=ctx.author.display_avatar)
        if (size := os.path.getsize(f"{title}.txt")) > 8 * 10 ** 6:
            bot.crawler_count = bot.crawler_count + 1
            if size > 32 * 10 ** 6 and int(bot.crawler[ctx.author.id].split("/")[1]) < 3000:
                os.remove(f"{title}.txt")
                bot.crawler_count = bot.crawler_count + 1
                return await ctx.send('Crawled file is too big. there is some problem in crawler')
            try:
                file = bot.mega.upload(f"{title}.txt")
                await ctx.send(
                    "Crawling Completed... Your novel is too big.We are uploading to Mega.. Please wait",
                    delete_after=5,
                )
                filelnk = bot.mega.get_upload_link(file)
                view = LinkView({"Novel": [filelnk, "📔"]})
                await ctx.reply(
                    content=f"> **✔{ctx.author.mention} your novel #{next_no} {title_name} is ready.**",
                    view=view,
                )
                channel = bot.get_channel(
                    1020980703229382706
                ) or await bot.fetch_channel(1020980703229382706)
                await channel.send(
                    embed=embed,
                    view=view, allowed_mentions=discord.AllowedMentions(users=False)
                )
                download_url = filelnk
            except Exception as e:
                print(e)
                await ctx.reply("> **❌Sorry the file is too big to send.**")
            os.remove(f"{title}.txt")
        else:
            file = discord.File(f"{title}.txt", f"{title_name[:100]}.txt")
            await ctx.reply(content=f"**🎉Here is your crawled novel #{next_no}**", file=file)
            channel = bot.get_channel(
                1020980703229382706
            ) or await bot.fetch_channel(1020980703229382706)

            msg = await channel.send(
                embed=embed,
                file=discord.File(f"{title}.txt"), allowed_mentions=discord.AllowedMentions(users=False)
            )
            download_url = msg.attachments[0].url
            try:
                file.close()
                os.remove(f"{title}.txt")
            except:
                pass
        if download_url and size > 0.3 * 10 ** 6:
            novel_data = [
                await bot.mongo.library.next_number,
                title_name,
                description,
                0,
                originallanguage,
                self.get_tags(title_name),
                download_url,
                size,
                ctx.author.id,
                datetime.datetime.utcnow().timestamp(),
                thumbnail,
                originallanguage,
                category
            ]
            data = Novel(*novel_data)
            try:
                await bot.mongo.library.add_novel(data)
            except:
                loop = True
                no_of_tries = 0
                while loop and no_of_tries < 6:
                    print(f"couldn't add to library... trying for {no_of_tries + 2} times")
                    try:
                        await asyncio.sleep(3)
                        data[0] = await bot.mongo.library.next_number
                        await bot.mongo.library.add_novel(data)
                        loop = False
                    except:
                        no_of_tries += 1
        return download_url
