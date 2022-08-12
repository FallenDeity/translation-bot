import concurrent.futures
import os
import typing as t
import zipfile

import aiofiles
import chardet
import discord
import docx
from discord.ext import commands

from core.bot import Raizel
from core.views.linkview import LinkView
from languages.terms import terms
from utils.translate import Translator


def checkName(name):
    spl = name.split("_")
    segment = 0
    for t in spl:
        if t[:-1].isalpha() and len(t) > 2:
            if len(t) > 4 or segment == 2:
                return True
            else:
                segment += 1
    return False


class Termer(commands.Cog):
    def __init__(self, bot: Raizel) -> None:
        self.bot = bot

    def term_raw(self, text, term_dict):
        # global term_dict
        for t in term_dict:
            text = text.replace(t, term_dict[t])
        return text

    @commands.command(
        help="Send along with ur novel txt or doc or link to auto translate. Currently supports only https://temp.sh",
        aliases=["term"],
    )
    async def termer(self, ctx, term, language: str = "english", *, link: str = None):
        string = [
            "{0: ^17}".format(f"{k} --> {v}") for k, v in self.bot.languages.items()
        ]
        string = "\n".join(
            ["".join(string[i : i + 3]) for i in range(0, len(string), 3)]
        )
        total = []
        for k, v in self.bot.languages.items():
            total.append(k)
            total.append(v)
        if link and ctx.message.attachments:
            return await ctx.reply(f"> **❌Send only an attachment or only a link.**")
        if ctx.message.attachments:
            link = None
        if term is None:
            return await ctx.reply(
                f"**Please Choose the validterms to be applied :\n\t"
                f"1 : Naruto \n\t2 : One-Piece \n\t3 : Pokemon\n\t4 : Mixed anime terms\n\t"
                f"5 : Prince of Tennis\n\t6 : Anime + Marvel + DC\n\t7 : Cultivation terms\n\t"
                f"8 : encoding converter \t"
            )
        else:
            term_dict = terms(term)
        if term_dict == {}:
            return await ctx.reply(
                f"**Please Choose the validterms to be applied :\n\t"
                f"1 : Naruto \n\t2 : One-Piece \n\t3 : Pokemon\n\t4 : Mixed anime terms\n\t"
                f"5 : Prince of Tennis\n\t6 : Anime + Marvel + DC\n\t7 : Cultivation terms\n\t"
            )
            # return await ctx.reply(f"select valid term")
        if language not in total and "http" not in language:
            return await ctx.reply(
                f"**❌We have the following languages in our db.**\n```ini\n{string}```"
            )
        if ctx.author.id in self.bot.translator:
            return await ctx.send("> **❌You cannot translate two novels at a time.**")
        if not ctx.message.attachments and not link:
            if language != "english":
                link = language
                language = "english"
            else:
                return await ctx.send("> **❌You must add a novel/link to translate**")
        await ctx.typing()
        if link:
            resp = await self.bot.con.get(link)
            try:
                file_type = "".join(
                    [
                        i
                        for i in resp.headers["Content-Disposition"].split(".")[-1]
                        if i.isalnum()
                    ]
                )
            except:
                view = LinkView({"Storage": ["https://temp.sh", "📨"]})
                return await ctx.send(
                    "> **❌Currently this link is not supported.**", view=view
                )
            name = link.split("/")[-1].replace(".txt", "").replace(".docx", "")
        else:
            name = (
                ctx.message.attachments[0]
                .filename.replace(".txt", "")
                .replace(".docx", "")
            )
            resp = await self.bot.con.get(ctx.message.attachments[0].url)
            file_type = resp.headers["content-type"].split("/")[-1]
        if "plain" in file_type.lower() or "txt" in file_type.lower():
            file_type = "txt"
        elif "document" in file_type.lower() or "docx" in file_type.lower():
            file_type = "docx"
        else:
            return await ctx.send("> **❌Only .docx and .txt supported**")
        data = await resp.read()
        async with aiofiles.open(f"{ctx.author.id}.{file_type}", "wb") as f:
            await f.write(data)
        if "docx" in file_type:
            await ctx.reply(
                "> **✔Docx file detected please wait while we finish converting.**"
            )
            await ctx.typing()
            doc = docx.Document(f"{ctx.author.id}.{file_type}")
            string = "\n".join([para.text for para in doc.paragraphs])
            async with aiofiles.open(
                f"{ctx.author.id}.txt", "w", encoding="utf-8"
            ) as f:
                await f.write(string)
            os.remove(f"{ctx.author.id}.docx")
        encoding = ["utf-8", "cp936", "utf-16", "cp949"]
        for i, j in enumerate(encoding):
            try:
                async with aiofiles.open(f"{ctx.author.id}.txt", "r", encoding=j) as f:
                    novel = await f.read()
                    break
            except:
                if i + 1 == len(encoding):
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
                continue
        await ctx.reply(f"> **✅Terming started. **")
        novel = self.term_raw(novel, term_dict)
        await ctx.reply(
            f"> **✅Terming completed ..Translation started. Translating to {language}.**"
        )
        os.remove(f"{ctx.author.id}.txt")
        liz = [novel[i : i + 1800] for i in range(0, len(novel), 1800)]
        self.bot.translator[ctx.author.id] = f"0/{len(liz)}"
        translate = Translator(self.bot, ctx.author.id, language)
        story = await translate.start(liz)
        async with aiofiles.open(f"{ctx.author.id}.txt", "w", encoding="utf-8") as f:
            await f.write(story)
        if os.path.getsize(f"{ctx.author.id}.txt") > 8 * 10**6:
            try:
                with zipfile.ZipFile(f"{ctx.author.id}.zip", "w") as jungle_zip:
                    jungle_zip.write(
                        f"{ctx.author.id}.txt", compress_type=zipfile.ZIP_DEFLATED
                    )
                filelnk = self.bot.drive.upload(filepath=f"{ctx.author.id}.zip")
                view = LinkView({"Novel": [filelnk.url, "📔"]})
                await ctx.reply(
                    f"> **✔{ctx.author.mention} your novel {name} is ready.**",
                    view=view,
                )
                channel = self.bot.get_channel(1005668482475643050)
                user = str(ctx.author)
                await channel.send(
                    f"> {name.replace('_',' ')} \nuploaded by {user} Termed novel: {term} language: {language}",
                    view=view,
                )
            except:
                await ctx.reply(
                    "**Sorry your file was too big please split it and try again.**"
                )
            os.remove(f"{ctx.author.id}.zip")
        else:
            file = discord.File(f"{ctx.author.id}.txt", f"{name}.txt")
            await ctx.reply("**🎉Here is your translated novel**", file=file)
            channel = self.bot.get_channel(1005668482475643050)
            user = str(ctx.author)
            await channel.send(
                f'> {name.replace("_"," ")} \nUploaded by {user} termed novel : {term} language: {language}',
                file=discord.File(f"{ctx.author.id}.txt", f"{name}.txt"),
            )
        os.remove(f"{ctx.author.id}.txt")
        del self.bot.translator[ctx.author.id]

    @commands.command(
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
