import discord
import aiofiles
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import os
import zipfile
import typing as t
from core.bot import Raizel
from discord.ext import commands


class Crawler(commands.Cog):

    def __init__(self, bot: Raizel) -> None:
        self.bot = bot

    @staticmethod
    def easy(nums: int, links: str) -> t.Tuple[int, str]:
        string = ""

        def stripper(lst: list) -> str:
            process = ''
            for r in lst:
                process += r.text.strip()
            return process

        blacklist = ['[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script']
        data = requests.get(links)
        soup = BeautifulSoup(data.content, 'lxml')
        if 'trxs' in links:
            text = soup.select('.read_chapterDetail')
            string += stripper(text)
        elif 'bixiange' in links:
            text = soup.select('.read_chapterDetail')
            string += stripper(text)
        elif 'tongrenquan' in links:
            text = soup.select('.read_chapterDetail')
            string += stripper(text)
        elif 'powanjuan' in links:
            text = soup.select('.content p')
            string += stripper(text)
        elif 'ffxs' in links:
            text = soup.select('.content p')
            string += stripper(text)
        else:
            text = soup.find_all(text=True)
            string += ''.join([i for i in text if i not in blacklist])
        print(string[:100])
        return nums, string

    def direct(self, urls: t.List[str], novel: t.Dict[int, str], name: int) -> dict:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.easy, i, j) for i, j in enumerate(urls)]
            for future in concurrent.futures.as_completed(futures):
                novel[future.result()[0]] = future.result()[1]
                self.bot.crawler[name] = f'{len(novel)}/{len(urls)}'
            return novel

    @commands.command(help='Gives progress of novel crawling', aliases=['cp'])
    async def crawled(self, ctx):
        if ctx.author.id not in self.bot.crawler:
            return await ctx.send("> **❌You have no novel deposited for crawling currently.**")
        await ctx.send(f"> **🚄`{self.bot.crawler[ctx.author.id]}`**")

    @commands.command(
        help='Crawls other sites for novels. Currently available trxs, tongrenquan, ffxs, bixiange, powanjuan, biqugeabc.')
    async def crawl(self, ctx, link=None):
        if ctx.author.id in self.bot.crawler:
            return await ctx.reply("> **❌You cannot crawl two novels at the same time.**")
        allowed = ['trxs', 'tongrenquan', 'ffxs', 'bixiange', 'powanjuan', 'biqugeabc']
        if link is None:
            return await ctx.reply(f"> **❌Enter a link for crawling.**")
        num = 0
        for i in allowed:
            if i not in link:
                num += 1
        if num == len(allowed):
            return await ctx.reply(f"> **❌We currently crawl only from {', '.join(allowed)}**")
        if link[-1] == '/':
            link = link[:-1]
        await ctx.typing()
        res = await self.bot.con.get(link)
        novel = {}
        soup = BeautifulSoup(await res.text(), 'html.parser')
        data = await res.read()
        soup1 = BeautifulSoup(data, 'lxml')
        title_name = str(soup1.find('title').string)
        title = f"{ctx.author.id}_crawl"
        name = str(link.split('/')[-1].replace('.html', ''))
        frontend_part = link.replace(f'/{name}', '').split('/')[-1]
        frontend = link.replace(f'/{name}', '').replace(f'/{frontend_part}', '')
        urls = [f'{frontend}{j}' for j in [str(i.get('href')) for i in soup.find_all('a')] if
                name in j and '.html' in j and 'txt' not in j]
        self.bot.crawler[ctx.author.id] = f'0/{len(urls)}'
        await ctx.reply(f"> **✔Crawl started.**")
        book = await self.bot.loop.run_in_executor(None, self.direct, urls, novel, ctx.author.id)
        print(book[5])
        parsed = {k: v for k, v in sorted(book.items(), key=lambda item: item[0])}
        whole = [i for i in list(parsed.values())]
        async with aiofiles.open(f'{title}.txt', 'w', encoding='utf-8') as f:
            await f.write("\n".join(whole))
        if os.path.getsize(f"{title}.txt") > 8 * 10 ** 6:
            try:
                with zipfile.ZipFile(f'{title}.zip', 'w') as jungle_zip:
                    jungle_zip.write(f'{title}.txt', compress_type=zipfile.ZIP_DEFLATED)
                filelnk = self.bot.drive.upload(filepath=f"{title}.zip")
                view = discord.ui.View()
                button = discord.ui.Button(label="Novel", style=discord.ButtonStyle.link, url=filelnk.url,
                                           emoji="📔")
                view.add_item(button)
                await ctx.reply(f"> **✔{ctx.author.mention} your novel {title_name} is ready.**", view=view)
            except:
                await ctx.reply("> **❌Sorry the file is too big to send.**")
            os.remove(f"{title}.zip")
        else:
            file = discord.File(f"{title}.txt", f"{title_name}.txt")
            await ctx.reply("**🎉Here is your crawled novel**", file=file)
        os.remove(f"{title}.txt")
        del self.bot.crawler[ctx.author.id]

    @commands.command(help='Clears any stagnant novels which were deposited for crawling.')
    async def cclear(self, ctx):
        if ctx.author.id in self.bot.crawler:
            del self.bot.crawler[ctx.author.id]
        files = os.listdir()
        for i in files:
            if str(ctx.author.id) in str(i) and 'crawl' in i:
                os.remove(i)
        await ctx.reply("> **✔Cleared all records.**")


async def setup(bot: Raizel) -> None:
    await bot.add_cog(Crawler(bot))
