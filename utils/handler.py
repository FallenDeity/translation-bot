import datetime
import os
import typing
import zipfile

import aiofiles
import chardet
import discord
import docx
from discord.ext import commands
from PyDictionary import PyDictionary
from textblob import TextBlob

from core.bot import Raizel
from core.views.linkview import LinkView
from databases.data import Novel


class FileHandler:

    ENCODING: list[str] = ["utf-8", "cp936", "utf-16", "cp949"]
    TOTAL: int = len(ENCODING)

    @staticmethod
    def get_tags(text: str) -> list[str]:
        text = text.replace("_", " ")
        text = TextBlob(text)
        return list(set(text.noun_phrases))

    @staticmethod
    def checkname(name):
        name = name.replace("-", "_")
        name = name.replace(" ", "_")
        name = name.replace("%20", "_")
        spl = name.split("_")
        dictionary = PyDictionary()
        segment = 0
        if len(spl)==1:
            return False
        for t in spl:
            if t is None or t == "":
                continue
            if not t[-1].isalpha():
                t = t[:-1]
            if (
                t[:-1].isalpha()
                and len(t) > 3
                and bool(dictionary.meaning(str(t), disable_errors=True))
            ):
                if len(t) > 6 or segment == 2:
                    return True
                else:
                    segment += 1
        return False

    @staticmethod
    async def docx_to_txt(ctx: commands.Context, file_type: str):
        await ctx.reply(
            "> **✔Docx file detected please wait while we finish converting.**"
        )
        await ctx.typing()
        doc = docx.Document(f"{ctx.author.id}.{file_type}")
        string = "\n".join([para.text for para in doc.paragraphs])
        async with aiofiles.open(f"{ctx.author.id}.txt", "w", encoding="utf-8") as f:
            await f.write(string)
        os.remove(f"{ctx.author.id}.docx")

    async def read_file(
        self, ctx: commands.Context
    ) -> typing.Union[str, discord.Message]:
        novel = None
        for i, j in enumerate(self.ENCODING):
            try:
                async with aiofiles.open(f"{ctx.author.id}.txt", "r", encoding=j) as f:
                    novel = await f.read()
                    break
            except UnicodeDecodeError:
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
        self, bot: Raizel, ctx: commands.Context, name: str, language: str, original_language: str
    ) -> None:
        download_url = None
        if (size := os.path.getsize(f"{ctx.author.id}.txt")) > 8 * 10**6:
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
                channel = bot.get_channel(1005668482475643050)
                user = str(ctx.author)
                await channel.send(
                    f"> {name.replace('_',' ')} \nuploaded by {user} Translated from: {original_language} to: {language}",
                    view=view,
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
            guild=bot.get_guild(940866934214373376)
            channel = guild.get_channel(1005668482475643050)
            user = str(ctx.author)
            msg = await channel.send(
                f'> {name.replace("_"," ")} \nUploaded by {user} Translated from: {original_language} to: {language}',
                file=discord.File(f"{ctx.author.id}.txt", f"{name}.txt"),
            )
            os.remove(f"{ctx.author.id}.txt")
            try:
                file.close()
            except:
                pass
            download_url = msg.attachments[0].url
        if download_url and size> 100000:
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
        del bot.translator[ctx.author.id]

    async def crawlnsend(
        self, ctx: commands.Context, bot: Raizel, title: str, title_name: str, originallanguage: str
    ) -> None:
        download_url = None
        if (size := os.path.getsize(f"{title}.txt")) > 8 * 10**6:
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
                download_url = filelnk
            except Exception as e:
                print(e)
                await ctx.reply("> **❌Sorry the file is too big to send.**")
            os.remove(f"{title}.txt")
        else:
            file = discord.File(f"{title}.txt", f"{title_name}.txt")
            msg = await ctx.reply("**🎉Here is your crawled novel**", file=file)
            download_url = msg.attachments[0].url
            os.remove(f"{title}.txt")
            try:
                file.close()
            except:
                pass
        if download_url and size> 100000:
            novel_data = [
                await bot.mongo.library.next_number,
                title_name,
                "",
                0,
                "chinese (simplified)",
                self.get_tags(title_name),
                download_url,
                size,
                ctx.author.id,
                datetime.datetime.utcnow().timestamp(),
                originallanguage,
            ]
            data = Novel(*novel_data)
            await bot.mongo.library.add_novel(data)
        del bot.crawler[ctx.author.id]
