import os
import typing

import aiofiles
import discord
from discord import app_commands
from discord.ext import commands
from mega import Mega

from core.bot import Raizel
from core.views.linkview import LinkView
from utils.handler import FileHandler
from utils.translate import Translator


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
        await ctx.send("Please wait.. Translation will began soon", delete_after=5)
        msg = None
        novel = None
        file_type = None
        name = None
        if ctx.message.attachments:
            link = ctx.message.attachments[0].url
        elif messageid is None and "mega.nz" in link:
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
            if "txt" not in file_type and "docx" not in file_type:
                os.remove(path)
                return await ctx.send("> **❌Only .docx and .txt supported**")
            name = name.replace(".txt", "").replace(".docx", "").replace(" ", "_")
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
        if "discord" in link:
            resp = await self.bot.con.get(link)
            if msg is None:
                msg = ctx.message
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
            name=name.replace("%20"," ")
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
        if novel is None:
            data = await resp.read()
            async with aiofiles.open(f"{ctx.author.id}.{file_type}", "wb") as f:
                await f.write(data)
            if "docx" in file_type:
                await FileHandler.docx_to_txt(ctx, file_type)
            novel = await FileHandler().read_file(ctx)
        await ctx.reply(f"> **✅Translation started. Translating to {language}.**")
        os.remove(f"{ctx.author.id}.txt")
        liz = [novel[i : i + 1800] for i in range(0, len(novel), 1800)]
        self.bot.translator[ctx.author.id] = f"0/{len(liz)}"
        translate = Translator(self.bot, ctx.author.id, language)
        story = await translate.start(liz)
        async with aiofiles.open(f"{ctx.author.id}.txt", "w", encoding="utf-8") as f:
            await f.write(story)
        await FileHandler().distribute(self.bot, ctx, name, language)

    @translate.autocomplete("language")
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
        for i in files:
            if str(ctx.author.id) in str(i) and "crawl" not in i:
                os.remove(i)
        await ctx.reply("> **✔Cleared all records.**")

    # @commands.hybrid_command(help="start mega", aliases=["start"])
    # async def mega(self, ctx: commands.Context):
    #     try:
    #         # print("userpwd:" + str(os.getenv("USER")) + str(os.getenv("MEGA")) + "'")
    #         self.bot.mega = Mega().login(
    #             email=os.getenv("USER").strip(), password=os.getenv("MEGA").strip()
    #         )
    #         await ctx.send("Mega login as user was successful")
    #         # user = self.bot.mega.get_user()
    #         # await ctx.send(str(user))
    #     except Exception as e:
    #         print(e)
    #         print(e.__traceback__.__str__())
    #         try:
    #             await ctx.send("login using mega failed. try logging inn anonymously")
    #             self.bot.mega = Mega().login()
    #         except:
    #             await ctx.send("Mega connection failed")
    #     await ctx.send(f"> **🚄`mega started`**")


async def setup(bot):
    await bot.add_cog(Translate(bot))
