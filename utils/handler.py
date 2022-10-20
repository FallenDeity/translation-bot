import datetime
import os
import random
import typing

import PyPDF2
import aiofiles
import chardet
import discord
import docx
import ebooklib
import parsel
from PyDictionary import PyDictionary
from deep_translator import single_detection
from discord.ext import commands
from ebooklib import epub
from textblob import TextBlob

from core.bot import Raizel
from core.views.linkview import LinkView
from databases.data import Novel
from languages import languages


def chapter_to_str(chapter):
    sel = parsel.Selector(str(chapter.get_content().decode()))
    text = sel.css("* ::text").extract()
    return "\n".join(text)

class FileHandler:
    ENCODING: list[str] = ["utf-8", "cp936", "utf-16", "cp949"]
    TOTAL: int = len(ENCODING)

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
    def find_language(text: str) -> str:
        api_keys = ['8ca7a29f3b7c8ac85487451129f35c89', '1c2d644450cb8923818607150e7766d4',
                    '5cd7b28759bb7aafe9b1d395824e7a67', 'af207e865e0277f375348293a30bcc5e']
        try:
            if "title_name " in text:
                text = text.replace("title_name ", "")
                lang_code = single_detection(str(text[:120]), api_key=random.choice(api_keys))
            else:
                lang_code = single_detection(text[200:400].__str__(), api_key=random.choice(api_keys))
        except:
            try:
                lang_code = single_detection(text[500:620].__str__(), api_key=random.choice(api_keys))
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
            original_Language = FileHandler.find_language(text[600:])
        else:
            try:
                original_Language = original_Language.pop()
            except:
                pass
        return original_Language

    @staticmethod
    def checkname(name: str, bot: Raizel):
        name = name.replace("-", "_")
        name = name.replace(" ", "_")
        name = name.replace("%20", "_")
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
    async def docx_to_txt(ctx: commands.Context, file_type: str):
        msg = await ctx.reply(
            "> **✔Docx file detected please wait while we finish converting.**"
        )
        doc = docx.Document(f"{ctx.author.id}.{file_type}")
        string = "\n".join([para.text for para in doc.paragraphs])
        async with aiofiles.open(f"{ctx.author.id}.txt", "w", encoding="utf-8") as f:
            await f.write(string)
        await msg.delete()
        os.remove(f"{ctx.author.id}.docx")

    @staticmethod
    async def epub_to_txt(ctx: commands.Context):
        msg=await ctx.reply("> **Epub file detected please wait till we finish converting to .txt")
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

    async def distribute(
            self, bot: Raizel, ctx: commands.Context, name: str, language: str, original_language: str, raw_name: str
    ) -> None:
        download_url = None
        if (size := os.path.getsize(f"{ctx.author.id}.txt")) > 8 * 10 ** 6:
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
                    f"> **✔{ctx.author.mention} your novel {name} is ready.**",
                    view=view,
                )
                if original_language == "korean":
                    channel = self.bot.get_channel(
                        1032638028868501554
                    ) or await self.bot.fetch_channel(1032638028868501554)
                else:
                    channel = self.bot.get_channel(
                        1005668482475643050
                    ) or await self.bot.fetch_channel(1005668482475643050)
                user = str(ctx.author)
                await channel.send(
                    f"> {name.replace('_', ' ')} \nuploaded by {user} {ctx.author.mention} Translated from: {original_language} to: {language}",
                    view=view, allowed_mentions=discord.AllowedMentions(users=False)
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
            await ctx.reply("**🎉Here is your translated novel**", file=file)
            if original_language == "korean":
                channel = self.bot.get_channel(
                    1032638028868501554
                ) or await self.bot.fetch_channel(1032638028868501554)
            else:
                channel = self.bot.get_channel(
                    1005668482475643050
                ) or await self.bot.fetch_channel(1005668482475643050)
            user = str(ctx.author)
            msg = await channel.send(
                f'> {name.replace("_", " ")} \nUploaded by {user} {ctx.author.mention} Translated from: {original_language} to: {language}',
                file=discord.File(f"{ctx.author.id}.txt", f"{name}.txt"), allowed_mentions=discord.AllowedMentions(users=False)
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
                "",
                0,
                language,
                self.get_tags(name),
                download_url,
                size,
                ctx.author.id,
                datetime.datetime.utcnow().timestamp(),
                original_language,
            ]
            data = Novel(*novel_data)
            await bot.mongo.library.add_novel(data)

    async def crawlnsend(
            self, ctx: commands.Context, bot: Raizel, title: str, title_name: str, originallanguage: str
    ) -> str:
        download_url = None
        if (size := os.path.getsize(f"{title}.txt")) > 8 * 10 ** 6:
            if size > 25 * 10 ** 6 and int(bot.crawler[ctx.author.id].split("/")[1]) < 2000:
                os.remove(f"{title}.txt")
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
                    f"> **✔{ctx.author.mention} your novel {title_name} is ready.**",
                    view=view,
                )
                channel = self.bot.get_channel(
                    1020980703229382706
                ) or await self.bot.fetch_channel(1020980703229382706)
                user = str(ctx.author)
                await channel.send(
                    f"> {title_name} \nCrawled by {user} {ctx.author.mention} Source language : {originallanguage}",
                    view=view, allowed_mentions=discord.AllowedMentions(users=False)
                )
                download_url = filelnk
            except Exception as e:
                print(e)
                await ctx.reply("> **❌Sorry the file is too big to send.**")
            os.remove(f"{title}.txt")
        else:
            file = discord.File(f"{title}.txt", f"{title_name}.txt")
            await ctx.reply("**🎉Here is your crawled novel**", file=file)
            channel = self.bot.get_channel(
                1020980703229382706
            ) or await self.bot.fetch_channel(1020980703229382706)
            user = str(ctx.author)
            msg = await channel.send(
                f'> {title_name} \nCrawled by {user} {ctx.author.mention} Source language : {originallanguage} ',
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
                "",
                0,
                originallanguage,
                self.get_tags(title_name),
                download_url,
                size,
                ctx.author.id,
                datetime.datetime.utcnow().timestamp(),
                originallanguage,
            ]
            data = Novel(*novel_data)
            await bot.mongo.library.add_novel(data)
        return download_url
