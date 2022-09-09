import os
import random
import typing

import aiofiles
import discord
from discord import app_commands
from discord.ext import commands
from deep_translator import single_detection

from core.bot import Raizel
from core.views.linkview import LinkView
from languages.terms import terms
from utils.handler import FileHandler
from utils.translate import Translator
from languages import languages


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
    ):
        file = link or file
        if not file and not messageid:
            return await ctx.reply(f"> **❌Send an attachment or a link.**")
        if language not in self.bot.all_langs and "http" not in language:
            return await ctx.reply(
                f"**❌We have the following languages in our db.**\n```ini\n{self.bot.display_langs}```"
            )
        if ctx.author.id in self.bot.translator:
            return await ctx.send("> **❌You cannot translate two novels at a time.**")
        if not ctx.message.attachments and not file and messageid is None:
            return await ctx.send("> **❌You must add a novel/link to translate**")
        msg = None
        novel = None
        file_type = None
        name = None
        await ctx.send("Please wait.. Translation will began soon", delete_after=5)
        if ctx.message.attachments:
            link = ctx.message.attachments[0].url
        elif messageid is None and ("mega.nz" in link or "mega.co.nz" in link):
            await ctx.send("Mega link found.... downloading from mega", delete_after=5)
            info = self.bot.mega.get_public_url_info(link)
            size = int(info.get("size")) / 1000
            if size >= 15 * 1000:
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
            name = name.replace(".txt", "").replace(".docx", "").replace(" ", "_")
            if "txt" not in file_type and "docx" not in file_type:
                os.remove(path)
                return await ctx.send("> **❌Only .docx and .txt supported**")
            name = name[:100]
            # os.rename(path, f"{ctx.author.id}.{file_type}")
            if "docx" in file_type:
                await FileHandler.docx_to_txt(ctx, file_type)
            novel = await FileHandler.read_file(FileHandler, ctx=ctx)
        else:
            if messageid is not None:
                messageId = messageid.split("/")[len(messageid.split("/")) - 1]
                # print(messageId)
                channel = self.bot.get_channel(ctx.channel.id)
                resolvedMessage = await channel.fetch_message(messageId)
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
            await ctx.send(f"> **✅Terming started. **", delete_after=5)
            term_dict = terms(term)
        if term_dict == {}:
            return await ctx.reply(
                f"**Please Choose the validterms to be applied :\n\t"
                f"1 : Naruto \n\t2 : One-Piece \n\t3 : Pokemon\n\t4 : Mixed anime terms\n\t"
                f"5 : Prince of Tennis\n\t6 : Anime + Marvel + DC\n\t7 : Cultivation terms\n\t"
            )
        if "discord" in link:
            if msg is None:
                msg = ctx.message
            resp = await self.bot.con.get(link)
            name = msg.attachments[0].filename.replace(".txt", "").replace(".docx", "")
            file_type = resp.headers["content-type"].split("/")[-1]
        elif novel is None:
            resp = await self.bot.con.get(link)
            try:
                file_type = FileHandler.get_headers(resp)
            except KeyError:
                view = LinkView({"Storage": ["https://temp.sh", "📨"]})
                return await ctx.send(
                    "> **❌Currently this link is not supported.**", view=view
                )
            name = link.split("/")[-1].replace(".txt", "").replace(".docx", "")
            name = name.replace("%20", " ")
        if "plain" in file_type.lower() or "txt" in file_type.lower():
            file_type = "txt"
        elif "document" in file_type.lower() or "docx" in file_type.lower():
            file_type = "docx"
        else:
            return await ctx.send("> **❌Only .docx and .txt supported**")
        if novelname is not None:
            name = novelname
        name_check = FileHandler.checkname(name)
        if not name_check:
            return await ctx.reply(
                f"> **❌{name} is not a valid novel name. please provide a valid name to filename before translating. **"
            )
        for tag in ['/', '\\', '<', '>', "'", '"', ':', ";", '?', '|', '*', ';']:
            name = name.replace(tag, '').strip()
        name = name.replace('_', ' ')
        if novel is None:
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
        api_keys=['8ca7a29f3b7c8ac85487451129f35c89', '1c2d644450cb8923818607150e7766d4', '5cd7b28759bb7aafe9b1d395824e7a67']
        lang_code = single_detection(novel[100:200].__str__(), api_key=random.choice(api_keys))
        if lang_code == 'zh':
            original_Language = ['chinese']
        else:
            lang = languages.choices
            original_Language = {i for i in lang if lang[i] == lang_code}
        try:
            original_Language = original_Language.pop()
        except:
            pass
        liz = [novel[i : i + 1800] for i in range(0, len(novel), 1800)]
        self.bot.translator[ctx.author.id] = f"0/{len(liz)}"
        translate = Translator(self.bot, ctx.author.id, language)
        story = await translate.start(liz)
        async with aiofiles.open(f"{ctx.author.id}.txt", "w", encoding="utf-8") as f:
            await f.write(story)
        await FileHandler().distribute(self.bot, ctx, name, language, original_Language)

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
