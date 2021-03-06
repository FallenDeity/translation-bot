import discord
import aiofiles
import concurrent.futures
import os
import chardet
import docx
import zipfile
import typing as t
from deep_translator import GoogleTranslator
from core.bot import Raizel
from discord.ext import commands


class Translator(commands.Cog):

    def __init__(self, bot: Raizel) -> None:
        self.bot = bot

    def translates(self, liz: t.List[str], order: t.Dict[int, str], author: int, lang: str) -> t.Dict[int, str]:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.download_image, [url], num, lang) for num, url in enumerate(liz)]
            for future in concurrent.futures.as_completed(futures):
                order[future.result()[0]] = future.result()[1]
                self.bot.translator[author] = f"{len(order)}/{len(liz)}"
            return order

    @staticmethod
    def download_image(img_url: t.List[str], num: int, lang: str) -> t.Tuple[int, t.List[str]]:
        translated = GoogleTranslator(source='auto', target=lang).translate_batch(img_url)
        return num, translated

    @commands.command(help='Gives progress of novel translation.', aliases=['now', 'n', 'p'])
    async def progress(self, ctx):
        if ctx.author.id not in self.bot.translator:
            return await ctx.send("> **❌You have no novel deposited for translation currently.**", delete_after=5)
        await ctx.send(f"> **🚄`{self.bot.translator[ctx.author.id]}`**")

    @commands.command(
        help='Send along with ur novel txt or doc or link to auto translate. Currently supports only https://temp.sh',
        aliases=['t'])
    async def translate(self, ctx, language: str = 'english', *, link: str = None):
        string = ["{0: ^17}".format(f"{k} --> {v}") for k, v in self.bot.languages.items()]
        string = '\n'.join([''.join(string[i:i + 3]) for i in range(0, len(string), 3)])
        total = []
        for k, v in self.bot.languages.items():
            total.append(k)
            total.append(v)
        if link and ctx.message.attachments:
            return await ctx.reply(f'> **❌Send only an attachment or only a link.**')
        if ctx.message.attachments:
            link = None
        if language not in total and 'http' not in language:
            return await ctx.reply(f"**❌We have the following languages in our db.**\n```ini\n{string}```")
        if ctx.author.id in self.bot.translator:
            return await ctx.send('> **❌You cannot translate two novels at a time.**')
        if not ctx.message.attachments and not link:
            if language != 'english':
                link = language
                language = 'english'
            else:
                return await ctx.send('> **❌You must add a novel/link to translate**')
        await ctx.typing()
        if link:
            resp = await self.bot.con.get(link)
            try:
                file_type = ''.join([i for i in resp.headers['Content-Disposition'].split('.')[-1] if i.isalnum()])
            except:
                view = discord.ui.View()
                button = discord.ui.Button(label="link", style=discord.ButtonStyle.link, url='https://temp.sh', emoji="📨")
                view.add_item(button)
                return await ctx.send("> **❌Currently this link is not supported.**", view=view)
            name = link.split('/')[-1].replace('.txt', '').replace('.docx', '')
        else:
            name = ctx.message.attachments[0].filename.replace('.txt', '').replace('.docx', '')
            resp = await self.bot.con.get(ctx.message.attachments[0].url)
            file_type = resp.headers['content-type'].split('/')[-1]
        if 'plain' in file_type.lower() or 'txt' in file_type.lower():
            file_type = 'txt'
        elif 'document' in file_type.lower() or 'docx' in file_type.lower():
            file_type = 'docx'
        else:
            return await ctx.send('> **❌Only .docx and .txt supported**')
        data = await resp.read()
        async with aiofiles.open(f'{ctx.author.id}.{file_type}', 'wb') as f:
            await f.write(data)
        if 'docx' in file_type:
            await ctx.reply('> **✔Docx file detected please wait while we finish converting.**')
            await ctx.typing()
            doc = docx.Document(f'{ctx.author.id}.{file_type}')
            string = '\n'.join([para.text for para in doc.paragraphs])
            async with aiofiles.open(f'{ctx.author.id}.txt', 'w', encoding='utf-8') as f: await f.write(string)
            os.remove(f'{ctx.author.id}.docx')
        encoding = ['utf-8', 'cp936', 'utf-16', 'cp949']
        for i, j in enumerate(encoding):
            try:
                async with aiofiles.open(f'{ctx.author.id}.txt', 'r', encoding=j) as f:
                    novel = await f.read()
                    break
            except:
                if i+1 == len(encoding):
                    try:
                        await ctx.send('> **✔Encoding not in db trying to auto detect please be patient.**')
                        async with aiofiles.open(f'{ctx.author.id}.txt', 'rb') as f:
                            novel = await f.read()
                        async with aiofiles.open(f'{ctx.author.id}.txt', 'r',
                                                 encoding=chardet.detect(novel[:500])['encoding'], errors='ignore') as f:
                            novel = await f.read()
                    except Exception as e:
                        print(e)
                        return await ctx.reply("> **❌Currently we are only translating korean and chinese.**")
                continue
        await ctx.reply(f'> **✅Translation started. Translating to {language}.**')
        os.remove(f'{ctx.author.id}.txt')
        liz = [novel[i:i + 1800] for i in range(0, len(novel), 1800)]
        order = {}
        self.bot.translator[ctx.author.id] = f"0/{len(liz)}"
        translated = await self.bot.loop.run_in_executor(None, self.translates, liz, order, ctx.author.id, language)
        comp = {k: v for k, v in sorted(translated.items(), key=lambda item: item[0])}
        full = [i[0] for i in list(comp.values()) if i[0] is not None]
        async with aiofiles.open(f'{ctx.author.id}.txt', 'w', encoding='utf-8') as f:
            await f.write(" ".join(full))
        if os.path.getsize(f"{ctx.author.id}.txt") > 8 * 10 ** 6:
            try:
                with zipfile.ZipFile(f'{ctx.author.id}.zip', 'w') as jungle_zip:
                    jungle_zip.write(f'{ctx.author.id}.txt', compress_type=zipfile.ZIP_DEFLATED)
                filelnk = self.bot.drive.upload(filepath=f"{ctx.author.id}.zip")
                view = discord.ui.View()
                button = discord.ui.Button(label="Novel", style=discord.ButtonStyle.link, url=filelnk.url,
                                           emoji="📔")
                view.add_item(button)
                await ctx.reply(f"> **✔{ctx.author.mention} your novel {name} is ready.**", view=view)
            except:
                await ctx.reply("**Sorry your file was too big please split it and try again.**")
            os.remove(f"{ctx.author.id}.zip")
        else:
            file = discord.File(f"{ctx.author.id}.txt", f"{name}.txt")
            await ctx.reply("**🎉Here is your translated novel**", file=file)
        os.remove(f"{ctx.author.id}.txt")
        del self.bot.translator[ctx.author.id]

    @commands.command(help='Clears any stagnant novels which were deposited for translation.')
    async def tclear(self, ctx):
        if ctx.author.id in self.bot.translator:
            del self.bot.translator[ctx.author.id]
        files = os.listdir()
        for i in files:
            if str(ctx.author.id) in str(i) and 'crawl' not in i:
                os.remove(i)
        await ctx.reply("> **✔Cleared all records.**")


async def setup(bot):
    await bot.add_cog(Translator(bot))
