import asyncio
import datetime
import os
import random
import re
import typing
from urllib.parse import urljoin
from collections import OrderedDict
from difflib import SequenceMatcher

from pypdf import PdfReader
import aiofiles
import chardet
import cloudscraper
import discord
import docx
import parsel
from PyDictionary import PyDictionary
from deep_translator import single_detection
from discord.ext import commands
# from epub2txt import epub2txt
from readabilipy import simple_json_from_html_string
from textblob import TextBlob
from bs4 import BeautifulSoup

from cogs.library import Library
from core.bot import Raizel
from core.views.linkview import LinkView
from databases.data import Novel
from languages import languages
from utils.category import Categories

from PIL import Image, ImageDraw


def chapter_to_str(chapter):
    sel = parsel.Selector(str(chapter.get_content().decode()))
    text = sel.css("* ::text").extract()
    return "\n".join(text)


class FileHandler:
    ENCODING: list[str] = ["utf-8", "cp936", "utf-16", "cp949"]
    TOTAL: int = len(ENCODING)

    @staticmethod
    def split_paragraphs(text, max_words=150):
        paragraphs = text.split("\n")
        new_paragraphs = []

        for paragraph in paragraphs:
            words = paragraph.split()
            if len(words) <= max_words * 1.8:
                new_paragraphs.append(paragraph)
            else:
                start = 0
                while start < len(words):
                    end = start + max_words
                    if end >= len(words):
                        new_paragraphs.append(" ".join(words[start:]))
                        break

                    # Find the end of the sentence
                    sentence_end = end
                    while sentence_end < len(words) and not words[sentence_end].endswith(('.', '!', '?')):
                        sentence_end += 1

                    # If no sentence end found within reasonable range, use max_words
                    if sentence_end >= len(words) or sentence_end > end + max_words // 2:
                        sentence_end = end

                    new_paragraphs.append(" ".join(words[start:sentence_end + 1]))
                    start = sentence_end + 1

        return "\n\n".join(new_paragraphs)

    @staticmethod
    async def checkLibrary(novel_data: list[Novel], title_name: str, title: str, originalLanguage: str,
                           ctx: commands.Context, bot: Raizel, ):
        if novel_data is not None:
            library = None
            novel_data = list(novel_data)
            if title_name:
                for subString in ["completed", "ongoing", "complete", "latest", "updated"]:
                    title_name = str(re.sub('(?i)' + re.escape(subString), lambda k: "", title_name))
            if title:
                for subString in ["completed", "ongoing", "complete", "latest", "updated"]:
                    title = str(re.sub('(?i)' + re.escape(subString), lambda k: "", title))
            name_lib_check = False
            ids = []
            for n in novel_data:
                ids.append(n._id)
                if title_name.strip('__')[0] in n.title:
                    name_lib_check = True
                org_str = re.sub("[^A-Za-z0-9]", "", title.split('__')[0]).lower()
                org_str2 = re.sub("[^A-Za-z0-9]", "", title.split('  ')[0]).lower()
                lib_str = re.sub("[^A-Za-z0-9]", "", n.title.split('__')[0]).lower()
                lib_str2 = re.sub("[^A-Za-z0-9]", "", n.title.split('  ')[0]).lower()
                if (title.split('__')[0].strip() == n.title.split('__')[0].strip()
                    or org_str == lib_str or org_str2 == lib_str
                    or lib_str2 == org_str2
                    or title_name.split('  ')[0].lower() == n.title.split('  ')[0].lower()
                    or (len(title) > 20 and org_str in lib_str)
                    or (len(title) > 20 and org_str2 in lib_str2)
                ) and originalLanguage in str(n.language).lower():
                    library = n._id
            if len(ids) >= 20:
                return None
            if True:
                ids = ids[:20]
                ctx.command = await bot.get_command("library search").callback(Library(bot), ctx,
                                                                               title_name.split('__')[0], None,
                                                                               None,
                                                                               None, None, None, None, None, None,
                                                                               False, "size", 20)
                if len(ids) < 5 or name_lib_check:
                    await ctx.send("**Please check from above library**", delete_after=20)
                    await asyncio.sleep(5)
                chk_msg = await ctx.send(embed=discord.Embed(
                    description=f"This novel **{title}** is already in our library with ids **{ids.__str__()}**...use arrow marks in above to navigate...\nIf you want to continue crawling react with 🇳 \n\n**Note : Some files are in docx format, so file size maybe half the size of txt. and try to minimize translating if its already in library**"))
                await chk_msg.add_reaction('🇾')
                await chk_msg.add_reaction('🇳')

                def check(reaction, user):
                    return reaction.message.id == chk_msg.id and (
                            str(reaction.emoji) == '🇾' or str(reaction.emoji) == '🇳') and user == ctx.author

                try:
                    res = await bot.wait_for(
                        "reaction_add",
                        check=check,
                        timeout=20.0,
                    )
                except asyncio.TimeoutError:
                    try:
                        os.remove(f"{ctx.author.id}.txt")
                    except:
                        pass
                    await ctx.send("No response detected.", delete_after=5)
                    await chk_msg.delete()
                    return 0
                else:
                    await ctx.send("Reaction received", delete_after=10)
                    await chk_msg.delete()
                    if str(res[0]) == '🇳':
                        msg = await ctx.reply("Reaction received.. please wait")
                        return library
                    else:
                        await ctx.send("Reaction received", delete_after=10)
                        try:
                            os.remove(f"{ctx.author.id}.txt")
                        except:
                            pass
                        await chk_msg.delete()
                        return 0
        else:
            return None

    @staticmethod
    def get_handler():
        user_agent_list: list[str] = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        ]
        return {'User-Agent': str(random.choice(user_agent_list))}

    @staticmethod
    async def update_status(bot: Raizel):
        if bot.is_closed():
            os.system("killall python3")
        try:
            if bot.app_status == "restart":
                await bot.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.playing,
                        name=f"Bot will restart soon. Please wait",
                    ),
                    status=discord.Status.do_not_disturb,
                )
                return
            if len(bot.translator) == 0 and len(bot.crawler) == 0 and len(bot.crawler_next) == 0:
                if random.randint(0, 10) > 5:
                    await bot.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.listening,
                            name=f"{len(bot.users)} novel enthusiasts. Prefix: .t",
                        ),
                        status=discord.Status.idle,
                    )
                else:
                    await bot.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.listening,
                            name=f"{await bot.mongo.library.next_number - 1} novels in library",
                        ),
                        status=discord.Status.idle,
                    )
                return
            else:
                outstr = []
                if len(bot.crawler) != 0:
                    outstr.append(f"crawling {len(bot.crawler)}")
                    if len(bot.translator) != 0 or len(bot.crawler_next) != 0:
                        outstr.append(" ,")
                if len(bot.crawler_next) != 0:
                    if len(bot.crawler) == 0:
                        outstr.append(f"crawling {len(bot.crawler_next)}")
                    else:
                        outstr.append(f", {len(bot.crawler_next)}")
                    if len(bot.translator) != 0:
                        outstr.append(" ,")
                outstr.append(" novels")
                if len(bot.translator) != 0:
                    outstr.append(f"translating {len(bot.translator)} novels")
                outstr.append("\n")
                if len(bot.crawler) != 0:
                    outstr.append("Crawler : ")
                    outstr.extend(
                        [f"{bot.get_user(keys).name}:{values}, " for keys, values in bot.crawler.items()])
                    # for keys, values in bot.crawler.items():
                    #     user = bot.get_user(keys)
                    #     user = user.name
                    #     outstr.append(f"{user}:{values}, ")
                    outstr.append("\n")
                if len(bot.crawler_next) != 0:
                    outstr.append("Crawlernext : ")
                    outstr.extend(
                        [f"{bot.get_user(keys).name}:{values}, " for keys, values in bot.crawler_next.items()])
                    # for keys, values in bot.crawler_next.items():
                    #     user = bot.get_user(keys)
                    #     user = user.name
                    #     outstr.append(f"{user}:{values}, ")
                    outstr.append("\n")
                if len(bot.translator) != 0:
                    outstr.append("Translator : ")
                    outstr.extend([f"{bot.get_user(keys).name}:{values}, " for keys, values in bot.translator.items()])
                    # for keys, values in bot.translator.items():
                    #     user = bot.get_user(keys)
                    #     user = user.name
                    #     outstr.append(f"{user}:{values}, ")
                output = "".join(outstr)
                if len(output) >= 128:
                    output = output[:123] + "..."
                await bot.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.watching, state="stat",
                        name=f"{output}",
                    ),
                    status=discord.Status.online,
                )
                return
        except:
            return

    @staticmethod
    async def find_urls_from_text(string):
        # findall() has been used
        # with valid conditions for urls in string
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        url = re.findall(regex, string)
        return [x[0] for x in url]

    @staticmethod
    async def distribute_genre(embed: discord.Embed, category: str, download_url: str, bot: Raizel):
        category_channels = {
            "Naruto": 1110761695174983680,
            "One-Piece": 1110761695174983680,
            "Harry-Potter": 1110761695174983680,
            "Pokemon": 1110761695174983680,
            "Fairy-Tail": 1110761695174983680,
            "Genshin-Impact": 1110761695174983680,
            "Doulou-Daluo": 1110761695174983680,
            "Conan": 1110761695174983680,
            "High-School-DXD": 1110761695174983680,
            "Hunter-X-Hunter": 1110761695174983680,
            "Doraemon": 1110761695174983680,
            "Dragon-Ball": 1110761695174983680,
            "Comprehensive": 1110761695174983680,
            "Yugi-Oh": 1110761695174983680,
            "Bleach": 1110761695174983680,
            "Shokugeki-No-Soma": 1110761695174983680,
            "Jackie-Chan": 1110761695174983680,
            "One-Punch-Man": 1110761695174983680,
            "Cartoonist": 1110761695174983680,
            "DC": 1110761272619839538,
            "Marvel": 1110761272619839538,
            "Villain": 1110764343869571132,
            "Fantasy": 1110761401930240030,
            "Spirit-Recovery": 1110761401930240030,
            "Reincarnation": 1110761401930240030,
            "R18": 1112230192522481754,
            "Technology": 1110761533631365220,
        }
        channel_id = category_channels.get(category)
        if channel_id is not None:
            channel = await bot.fetch_channel(channel_id)
            view = LinkView({"Novel": [download_url, await FileHandler.get_emoji_book()]})
            await channel.send(embed=embed, view=view)

    @staticmethod
    async def get_emoji_book() -> str:
        return random.choice(["📖", "📗", "📘", "📙", "📕", "📔", "📔"])

    @staticmethod
    async def get_regex_from_name(title: str) -> str:
        return re.sub(r'(\.\*)\1+', r"\1", re.sub(r'[^a-zA-Z]', '.*', title))
        # output = ''
        # prev_check = True
        # for i in title:
        #     if i.isalpha():
        #         output += i
        #         prev_check = True
        #     elif prev_check:
        #         output += ".*"
        #         prev_check = False
        # return output

    @staticmethod
    async def get_desc_from_text(text: str, title: str = None, link: str = ""):
        desc = ["introduction", "description", "简介", "描述", "描写", "summary", "prologue", "概括", "摘要", "总结",
                "序幕", "开场白", "loadAdv(2,0)"]
        text = '\n'.join(OrderedDict.fromkeys(text.split('\n')))  # remove  duplicate lines from description
        if "69shu" in link:
            desc.append("loadAdv(2,0)")
            desc.append("chapter")
        if title:
            text = re.sub(re.compile(await FileHandler.get_regex_from_name(title), flags=re.IGNORECASE), "",
                          text)  # remove title from description
        if "69shu.com" in text or "jiu mu" in text.lower() or "jiumu" in text.lower():
            desc.append("chapter")
        text = re.sub(re.compile("for more novels \([0-9]*\) join: https://discord.gg/[a-zA-Z]*"), "", text)
        text = str(re.sub(r'^https?:\/\/.*[\r\n]*', '', text.replace("source :", "").replace("Source :", "").strip(),
                          flags=re.MULTILINE))
        for d in desc:
            if d in text.lower():
                description = re.split(d, text, flags=re.IGNORECASE, maxsplit=1)[1][:500]
                description = ((re.sub(r'(\n\s*)+\n', '\n', description).strip()).strip(":")).strip().strip(":")
                return description
        return re.sub(r'(\n\s*)+\n', '\n', text[:500].strip())

    @staticmethod
    async def get_description(soup: "BeautifulSoup", link: str = "empty", next: str = None, title: str = None) -> str:
        aliases = ("description", "Description", "DESCRIPTION", "desc", "Desc", "DESC")
        description = ""
        if next:
            scraper = cloudscraper.CloudScraper(delay=10)
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
            scraper = cloudscraper.CloudScraper(delay=10)  # CloudScraper inherits from requests.Session
            href = urljoin(link, parsel.Selector(scraper.get(link).text).css("div.titxt ::attr(href)").extract_first())
            response = scraper.get(href)
            response.encoding = response.apparent_encoding
            description = "\n".join(parsel.Selector(response.text).css("div.navtxt ::text").extract())
            description = await FileHandler.get_desc_from_text(description, title)
            if description is not None and description.strip() != "":
                return description
        for meta in soup.find_all("meta"):
            if meta.get("name", "") in aliases:
                description += meta.get("content", "")
        if description is None:
            description = ""
        return description

    @staticmethod
    async def get_tags(text: str) -> list[str]:
        text = text.replace("_", " ")
        text = TextBlob(text)
        return list(set(text.noun_phrases))

    @staticmethod
    async def get_language(lang_code: str) -> str:
        lang = languages.choices
        if lang_code in lang:
            language = {lang_code}
        else:
            language = {i for i in lang if lang[i] == lang_code}
        return language.pop()

    @staticmethod
    async def find_language(text: str, link: str = None) -> str:
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
            original_Language = await FileHandler.find_language(text[600:700])

        try:
            original_Language = original_Language.pop()
        except:
            try:
                original_Language = original_Language.replace("['", "").replace("']", "")
            except:
                pass
        return original_Language

    @staticmethod
    async def checkname(name: str, bot: Raizel):
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
            if t.lower() in bot.dictionary or (len(t) > 3
                                               and bool(dictionary.meaning(str(t), disable_errors=True))):
                if len(t) > 5 or segment >= 2:
                    return True
                else:
                    segment += 1
        return False

    @staticmethod
    async def find_toc_next(soup: BeautifulSoup, link: str = None):
        selectors = ("下一页", "next page", ">", "next", "»»", "»", "下一节", "后一页")  # 下一页  "下一章"- next chp 下一页
        for a in soup.find_all("a"):
            # print(a.get('href'))
            if any(selector == a.get_text().lower() for selector in selectors):
                # print("toc true")
                return urljoin(link, a.get('href'))
        print("tocfalse")
        return None

    @staticmethod
    def find_next_chps(soup: BeautifulSoup, link: str = None):
        selectors = (
            "下一页", "next page", "下一章", "next chapter", "next", "Вперёд »»", "Вперёд", "»»", "»", "下一节",
            "后一页",
            "chương sau", "next>>", "下一頁", "下章")  # 下一页  "下一章"- next chp 下一页
        for a in soup.find_all("a"):
            # print(a.get_text())
            if any(selector == a.get_text().lower().strip() for selector in selectors):
                # print("next true")
                return urljoin(link, a.get('href'))
        return None

    @staticmethod
    async def docx_to_txt(ctx: commands.Context, file_type: str):
        msg = await ctx.reply(
            "> **✔Docx file detected please wait while we finish converting.**"
        )
        try:
            doc = docx.Document(f"{ctx.author.id}.{file_type}")
            string = "\n".join([para.text for para in doc.paragraphs])
            async with aiofiles.open(f"{ctx.author.id}.txt", "w", encoding="utf-8") as f:
                await f.write(string)
            await msg.delete()
            os.remove(f"{ctx.author.id}.docx")
        except Exception as e:
            await ctx.send("error occured in converting docx to txt")

    @staticmethod
    async def get_title(soup: BeautifulSoup) -> str:
        for tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            try:
                if title := soup.select_one(tag):
                    return title.get_text().strip()
            except Exception:
                pass
        return ""

    @staticmethod
    async def epub_to_txt(ctx: commands.Context):
        msg = await ctx.reply("> **Epub file detected please wait till we finish converting to .txt")
        raise Exception("Failed to convert epub")
        # try:
        #     filepath = f"{ctx.author.id}.epub"
        #     res = epub2txt(filepath)
        #     with open(f"{ctx.author.id}.txt", "w", encoding="utf-8") as f:
        #         f.write(res)
        #     await msg.delete()
        #     os.remove(f"{ctx.author.id}.epub")
        # except Exception as e:
        #     await ctx.reply("> Epub to txt conversion failed")
        #     raise e

    @staticmethod
    async def pdf_to_txt(ctx: commands.Context):
        msg = await ctx.reply("> **PDF file detected. converting to txt")
        pdfReader = PdfReader(f'{ctx.author.id}.pdf')
        full_text = ""
        for i in range(0, len(pdfReader.pages)):
            pageObj = pdfReader.pages[i]
            full_text += pageObj.extract_text()
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
                        # .bot.logger.info(f"Error occurred {e} {e.__traceback__}")
                        return await ctx.reply(
                            "> **❌Currently we are only translating korean and chinese.**"
                        )
        return novel

    @staticmethod
    async def get_headers(response) -> str:
        string = "".join(
            [
                i
                for i in response.headers["Content-Disposition"].split(".")[-1]
                if i.isalnum()
            ]
        )
        return string

    @staticmethod
    async def tokenize(link: str) -> tuple[str, ...]:
        url = link.replace(".html", "").replace(".htm/", "")
        suffix = url.split("/")[-1]
        midfix = url.replace(f"/{suffix}", "").split("/")[-1]
        prefix = url.replace(f"/{midfix}/{suffix}", "")
        return url, suffix, midfix, prefix

    @staticmethod
    async def drawProgressBar(progress, fname: str, x=10, y=10, w=450, h=20, bg="black", fg="red"):
        out = Image.new("RGBA", (500, 30), (0, 0, 0, 0))
        d = ImageDraw.Draw(out)
        # draw background
        d.ellipse((x + w, y, x + h + w, y + h), fill=bg)
        d.ellipse((x, y, x + h, y + h), fill=bg)
        d.rectangle((x + (h / 2), y, x + w + (h / 2), y + h), fill=bg)

        # draw progress bar
        w *= progress
        d.ellipse((x + w, y, x + h + w, y + h), fill=fg)
        d.ellipse((x, y, x + h, y + h), fill=fg)
        d.rectangle((x + (h / 2), y, x + w + (h / 2), y + h), fill=fg)
        os.makedirs("img", exist_ok=True)
        out.save(f"img/{fname}.png")

    async def get_thumbnail(self, soup, link) -> str:
        scraper = cloudscraper.create_scraper(delay=10)
        if "69shu" in link and "txt" not in link:
            link = urljoin(link, parsel.Selector(scraper.get(link).text).css("div.titxt ::attr(href)").extract_first())
            soup = BeautifulSoup(scraper.get(link).text, "html.parser")
        url, suffix, midfix, prefix = await FileHandler.tokenize(link)
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
                    if "images/logo.png" in img or "logo.png" in img:
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
            if i.get("property", None) == "og:image":
                return urljoin(link, i.get("content", ""))
        for i in meta:
            if i.get("property", None) == "twitter:image" or "image" in i.get("property", None):
                return urljoin(link, i.get("content", ""))
        return ""

    async def get_og_image(self, soup: BeautifulSoup, link: str):
        meta = soup.find_all("meta")
        for i in meta:
            print(i)
            if i is None or i.get("property", None) is None:
                continue
            if i.get("property", None) == "og:image" or "image" in i.get("property", None):
                return urljoin(link, i.get("content", ""))
        return await FileHandler().get_thumbnail(soup, link)

    async def distribute(
            self, bot: Raizel, ctx: commands.Context, name: str, language: str, original_language: str, raw_name: str,
            description: str = "", thumbnail: str = "", library: int = None, novel_url: str = None
    ) -> None:
        download_url = None
        update: bool = True
        if library is None:
            next_no = await bot.mongo.library.next_number
        else:
            next_no = library
        category = "Uncategorised"
        name = name.split("ex=65")[0]
        try:
            category = Categories.from_string(f"{name}")
            if category == "Uncategorised" and not description == "":
                category = Categories.from_string(f"{name} {description}")
            if thumbnail is None or thumbnail.strip() == "":
                thumbnail = Categories.thumbnail_from_category(category)
        except Exception as e:
            bot.logger.info(f"error occurred when getting thumbnail {e} {e.__traceback__}")
            print("exception in  getting category")
            print(e)
            if thumbnail.strip() == "":
                thumbnail = Categories.thumbnail_from_category(category)
        embed = discord.Embed(title=str(f"#{next_no} : " + name[:240]), description=f"```yaml\n{description[:350]}```",
                              colour=discord.Colour.dark_gold())
        embed.add_field(name="Category", value=category)
        embed.add_field(name="Language", value=language)
        if novel_url:
            embed.add_field(name="Crawled from", value=novel_url)
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f"Uploaded by {ctx.author}", icon_url=ctx.author.display_avatar)
        size = os.path.getsize(f"{ctx.author.id}.txt")
        if size < 25 * 10 ** 6:
            if original_language.lower() == "korean" and language.lower() == "english":
                channel = bot.get_channel(
                    1086592167767711794
                ) or await bot.fetch_channel(1086592167767711794)
            elif language.lower() == "english":
                channel = bot.get_channel(
                    1086593341740818523
                ) or await bot.fetch_channel(1086593341740818523)
            else:
                channel = bot.get_channel(
                    1155398011229327400
                ) or await bot.fetch_channel(1155398011229327400)
            msg = await channel.send(
                embed=embed, file=discord.File(f"{ctx.author.id}.txt", f"{name}.txt"),
                allowed_mentions=discord.AllowedMentions(users=False)
            )
            download_url = msg.attachments[0].url
        if size > 0:
            try:
                await ctx.send(
                    "We are uploading to Mega.. Please wait",
                    delete_after=5,
                )
                embed.add_field(name="size", value=f"{round(size / (1024 ** 2), 2)} MB")
                # filename = f"{random.choice(string.ascii_letters)}{random.choice(string.digits)}{str(
                # ctx.author.id)}_" \ f"trans{random.choice(string.ascii_letters)}{random.randint(100,1000)}.txt"
                file = await bot.loop.run_in_executor(None, bot.mega.upload, f"{ctx.author.id}.txt", None,
                                                      f"{name[:100]}.txt")
                filelnk = await bot.loop.run_in_executor(None, bot.mega.get_upload_link, file)
                if size >= 25 * 10 ** 6:
                    view = LinkView({"Novel": [filelnk, await self.get_emoji_book()]})
                    if original_language.lower() == "korean":
                        channel = bot.get_channel(
                            1086592167767711794
                        ) or await bot.fetch_channel(1086592167767711794)
                    elif language.lower() == "english":
                        channel = bot.get_channel(
                            1086593341740818523
                        ) or await bot.fetch_channel(1086593341740818523)
                    else:
                        channel = bot.get_channel(
                            1086593341740818523
                        ) or await bot.fetch_channel(1086593341740818523)
                    await channel.send(
                        embed=embed, view=view, allowed_mentions=discord.AllowedMentions(users=False)
                    )
                download_url = filelnk
            except Exception as e:
                print(e)
                bot.logger.info(f"Error occurred {e} {e.__traceback__}")
                await ctx.reply(
                    "**Sorry your file was too big and mega seems down now. ping developers in support server to resolve the issue.. please split it and try again.**" + e[
                                                                                                                                                                         :1000] + ""
                )
            try:
                os.remove(f"{ctx.author.id}.txt")
            except:
                pass

        try:
            os.remove(f"{ctx.author.id}.txt")
        except:
            pass
        bot.translation_count = bot.translation_count + (round(size / (1024 ** 2), 2) / 3.1)
        if raw_name is not None:
            name = name + "__" + raw_name
        try:
            if language == "english":
                embed.add_field(name="size", value=f"{round(size / (1024 ** 2), 2)} MB")
                await self.distribute_genre(embed, category, download_url, bot)
        except:
            pass
        if library is not None:
            data = await bot.mongo.library.get_novel_by_id(library)
            if size + 1000 < data['size']:
                update = False
                s = SequenceMatcher(None, data['description'], description)
                if s.ratio() <= 0.7:
                    library = None
        if library is None:
            if download_url and size > 0.3 * 10 ** 6:
                novel_data = [
                    await bot.mongo.library.next_number,
                    name,
                    description,
                    0,
                    language,
                    await self.get_tags(name),
                    download_url,
                    size,
                    ctx.author.id,
                    datetime.datetime.now(datetime.timezone.utc).timestamp(),
                    # datetime.datetime.utcnow().timestamp(),
                    thumbnail,
                    original_language,
                    category,
                    novel_url
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
                            next_no = data[0]
                            await bot.mongo.library.add_novel(data)
                            loop = False
                        except:
                            no_of_tries += 1
        elif update:
            await bot.mongo.library.update_novel_(_id=library, title=name, description=description,
                                                  download=download_url, size=size,
                                                  date=datetime.datetime.now(datetime.timezone.utc).timestamp(),
                                                  thumbnail=thumbnail, category=category, crawled_from=novel_url)
        view = LinkView({"Novel": [download_url, await self.get_emoji_book()]})
        await ctx.reply(content=f"> **{ctx.author.mention} 🎉Here is your translated novel #{next_no} {name}**",
                        view=view)
        return

    async def crawlnsend(
            self, ctx: commands.Context, bot: Raizel, title: str, title_name: str, originallanguage: str,
            description: str = "", thumbnail: str = "", link: str = None, library: int = None
    ) -> str:
        download_url = None
        update: bool = True
        if library is None:
            next_no = await bot.mongo.library.next_number
        else:
            next_no = library
        category = "Uncategorised"
        title = title.split("ex=65")[0]
        title_name = title_name.split("ex=65")[0]
        bot.crawler_count = bot.crawler_count + 1
        if description is None:
            description = ""
        try:
            category = Categories.from_string(f"{title}")
            if category == "Uncategorised" and not description == "":
                category = Categories.from_string(f"{title} {description}")
            if thumbnail.strip() == "":
                thumbnail = Categories.thumbnail_from_category(category)
        except Exception as e:
            bot.logger.info(f"Error occurred {e} {e.__traceback__}")
            print("exception in  getting category")
            print(e)
            if thumbnail.strip() == "":
                thumbnail = Categories.thumbnail_from_category(category)
        embed = discord.Embed(title=str(f"#{next_no} : " + title[:240]), description=f"```yaml\n{description[:350]}```",
                              colour=discord.Colour.dark_gold())
        embed.add_field(name="Category", value=category)
        embed.add_field(name="Language", value=originallanguage)
        if link:
            embed.add_field(name="Crawled from :", value=f"{link}")
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f"Uploaded by {ctx.author}", icon_url=ctx.author.display_avatar)
        if originallanguage == "english":
            channel_id = 1086593341740818523
        else:
            channel_id = 1086592655238103061

        if (size := os.path.getsize(f"{ctx.author.id}_cr.txt")) < 25 * 10 ** 6:
            channel = bot.get_channel(
                channel_id
            ) or await bot.fetch_channel(channel_id)

            msg = await channel.send(
                embed=embed,
                file=discord.File(f"{ctx.author.id}_cr.txt", f"{title}.txt"),
                allowed_mentions=discord.AllowedMentions(users=False)
            )
            download_url = msg.attachments[0].url
        if size > 0:
            bot.crawler_count = bot.crawler_count + 1
            # if size :
            #     os.remove(f"{ctx.author.id}_cr.txt")
            #     bot.crawler_count = bot.crawler_count + 1
            #     return await ctx.send('Crawled file is too big. there is some problem in crawler')
            try:
                # filename = f"{random.choice(string.ascii_letters)}{random.choice(string.digits)}{str(ctx.author.id)}_" \
                #            f"trans{random.choice(string.ascii_letters)}{random.randint(100, 1000)}.txt"
                file = await bot.loop.run_in_executor(None, bot.mega.upload, f"{ctx.author.id}_cr.txt", None,
                                                      f"{title_name[:100]}.txt")
                await ctx.send(
                    "We are uploading to Mega.. Please wait",
                    delete_after=5,
                )
                try:
                    os.remove(f"{ctx.author.id}_cr.txt")
                except:
                    pass
                embed.add_field(name="size", value=f"{round(size / (1024 ** 2), 2)} MB")
                filelnk = await bot.loop.run_in_executor(None, bot.mega.get_upload_link, file)
                if size >= 25 * 10 ** 6:
                    view = LinkView({"Novel": [filelnk, await self.get_emoji_book()]})
                    channel = bot.get_channel(
                        channel_id
                    ) or await bot.fetch_channel(channel_id)
                    await channel.send(
                        embed=embed,
                        view=view, allowed_mentions=discord.AllowedMentions(users=False)
                    )
                download_url = filelnk
            except Exception as e:
                bot.logger.info(f"Error occurred {e} {e.__traceback__}")
                print(e)
                await ctx.reply(
                    "> **❌Sorry the file is too big to send and mega seems down now. ping developers in support server to resolve the issue..**" + e[
                                                                                                                                                   :1000] + "")
            try:
                os.remove(f"{ctx.author.id}_cr.txt")
            except:
                pass

        if library is not None:
            data = await bot.mongo.library.get_novel_by_id(library)
            if size + 1000 < data['size']:
                update = False
                s = SequenceMatcher(None, data['description'], description)
                if s.ratio() <= 0.7:
                    library = None
        if library is None:
            if download_url and size > 0.3 * 10 ** 6:
                novel_data = [
                    await bot.mongo.library.next_number,
                    title_name,
                    description,
                    0,
                    originallanguage,
                    await self.get_tags(title_name),
                    download_url,
                    size,
                    ctx.author.id,
                    datetime.datetime.now(datetime.timezone.utc).timestamp(),
                    # datetime.datetime.utcnow().timestamp(),
                    thumbnail,
                    originallanguage,
                    category,
                    link
                ]
                data = Novel(*novel_data)
                try:
                    await bot.mongo.library.add_novel(data)
                except Exception as e:
                    loop = True
                    no_of_tries = 0
                    while loop and no_of_tries < 6:
                        bot.logger.info(f"Error occurred {e} {e.__traceback__}")
                        bot.logger.info(f"couldn't add to library... trying for {no_of_tries + 2} times")
                        try:
                            await asyncio.sleep(3)
                            data[0] = await bot.mongo.library.next_number
                            next_no = int(data[0])
                            await bot.mongo.library.add_novel(data)
                            loop = False
                        except:
                            no_of_tries += 1
        elif update:
            await bot.mongo.library.update_novel_(_id=library, title=title_name, description=description,
                                                  download=download_url, size=size,
                                                  date=datetime.datetime.now(datetime.timezone.utc).timestamp(),
                                                  thumbnail=thumbnail, category=category, crawled_from=link)

        if originallanguage == "english":
            embed.add_field(name="size", value=f"{round(size / (1024 ** 2), 2)} MB")
            await self.distribute_genre(embed, category, download_url, bot)
        view = LinkView({"Novel": [download_url, await self.get_emoji_book()]})
        await ctx.reply(
            content=f"> **{ctx.author.mention} 🎉Here is your crawled novel #{next_no} {title.split('__')[0]}**  size : {round(size / (1024 ** 2), 2)} MB",
            view=view)
        return download_url
