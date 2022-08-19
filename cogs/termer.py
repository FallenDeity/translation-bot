import os
import typing

import aiofiles
import discord
from discord import app_commands
from discord.ext import commands

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
        help="Replace terms in a text with the command. For large files use temp.sh.",
        aliases=["term"],
    )
    async def termer(
        self,
        ctx,
        term: str = None,
        link: str = None,
        file: typing.Optional[discord.Attachment] = None,
        language: str = "english",
    ):
        file = link or file
        if not file:
            return await ctx.reply(f"> **❌Send an attachment or a link.**")
        if language not in self.bot.all_langs and "http" not in language:
            return await ctx.reply(
                f"**❌We have the following languages in our db.**\n```ini\n{self.bot.display_langs}```"
            )
        if ctx.author.id in self.bot.translator:
            return await ctx.send("> **❌You cannot translate two novels at a time.**")
        if not ctx.message.attachments and not file:
            return await ctx.send("> **❌You must add a novel/link to translate**")
        if ctx.message.attachments:
            link = ctx.message.attachments[0].url
        else:
            if isinstance(file, discord.Attachment):
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
            term_dict = terms(term)
        if term_dict == {}:
            return await ctx.reply(
                f"**Please Choose the validterms to be applied :\n\t"
                f"1 : Naruto \n\t2 : One-Piece \n\t3 : Pokemon\n\t4 : Mixed anime terms\n\t"
                f"5 : Prince of Tennis\n\t6 : Anime + Marvel + DC\n\t7 : Cultivation terms\n\t"
            )
        if "discord" in link:
            resp = await self.bot.con.get(link)
            name = (
                ctx.message.attachments[0]
                .filename.replace(".txt", "")
                .replace(".docx", "")
            )
            file_type = resp.headers["content-type"].split("/")[-1]
        else:
            resp = await self.bot.con.get(link)
            try:
                file_type = FileHandler.get_headers(resp)
            except KeyError:
                view = LinkView({"Storage": ["https://temp.sh", "📨"]})
                return await ctx.send(
                    "> **❌Currently this link is not supported.**", view=view
                )
            name = link.split("/")[-1].replace(".txt", "").replace(".docx", "")
        if "plain" in file_type.lower() or "txt" in file_type.lower():
            file_type = "txt"
        elif "document" in file_type.lower() or "docx" in file_type.lower():
            file_type = "docx"
        else:
            return await ctx.send("> **❌Only .docx and .txt supported**")
        namecheck = FileHandler.checkname(name)
        if not namecheck:
            return await ctx.reply(
                f"> **❌{name} is not a valid novel name. please provide a valid name to filename before translating. **"
            )
        data = await resp.read()
        async with aiofiles.open(f"{ctx.author.id}.{file_type}", "wb") as f:
            await f.write(data)
        if "docx" in file_type:
            await FileHandler.docx_to_txt(ctx, file_type)
        novel = await FileHandler().read_file(ctx)
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
        await FileHandler().distribute(self.bot, ctx, name, language)

    @termer.autocomplete("language")
    async def translate_complete(
        self, inter: discord.Interaction, language: str
    ) -> list[app_commands.Choice]:
        lst = [i for i in self.bot.all_langs if language.lower() in i.lower()][:25]
        return [app_commands.Choice(name=i, value=i) for i in lst]

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
