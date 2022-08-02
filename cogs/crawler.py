import discord
import aiofiles
import requests

import parsel
from bs4 import BeautifulSoup
import concurrent.futures
import os
import zipfile
import typing as t
from core.bot import Raizel
from discord.ext import commands
from deep_translator import GoogleTranslator

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
}


def findURLCSS(link):
    if 'trxs' in link:
        return '.read_chapterDetail p ::text'
    if 'tongrenquan' in link:
        return '.read_chapterDetail p ::text'
    if 'bixiange' in link:
        return '.read_chapterDetail p ::text'
    if 'qbtr' in link:
        return '.read_chapterDetail p ::text'
    if 'jpxs' in link:
        return '.read_chapterDetail p ::text'
    if 'powanjuan' in link:
        return '.content p::text'
    if 'ffxs' in link:
        return '.content p::text'
    if 'sjks' in link:
        return '.content p::text'
    if 'sj.uukanshu' in link:
        return 'p ::text'
    if 'uukanshu.cc' in link:
        return '.bbb.font-normal.readcotent ::text'
    if 'biqugeabc' in link:
        return '.text_row_txt >p ::text'
    if 'uuks' in link:
        return 'div#contentbox > p ::text'
    else:
        return '*::text'


def findchptitlecss(link):
    if 'trxs' in link:
        return [".infos>h1:first-child", '']
    if 'tongrenquan' in link:
        return [".infos>h1:first-child", '']
    if 'bixiange' in link:
        return [".infos>h1:first-child", '']
    if 'qbtr' in link:
        return [".infos>h1:first-child", '']
    if 'jpxs' in link:
        return [".infos>h1:first-child", '']
    if 'powanjuan' in link:
        return [".desc >h1", '']
    if 'ffxs' in link:
        return [".desc >h1", '']
    if 'sjks' in link:
        return [".box-artic>h1", '']
    if 'sj.uukanshu' in link:
        return ['.bookname', '#divContent >h3 ::text']
    if 'uukanshu.cc' in link:
        return ['.booktitle', 'h1 ::text']
    if 'biqugeabc' in link:
        return [".top>h1", '.reader-main .title ::text']
    if 'uuks' in link:
        return [".jieshao_content>h1", 'h1#timu ::text']
    else:
        return ['title', '']


class Crawler(commands.Cog):

    def __init__(self, bot: Raizel) -> None:
        self.titlecss = None
        self.chptitlecss = None
        self.urlcss = None
        self.bot = bot

    @staticmethod
    def easy(nums: int, links: str, css, chptitleCSS) -> t.Tuple[int, str]:
        response = requests.get(links, headers=headers)
        response.encoding = response.apparent_encoding
        html = response.text
        sel = parsel.Selector(html)
        text = sel.css(css).extract()
        full = ''
        if not chptitleCSS == '':
            try:
                chpTitle = sel.css(chptitleCSS).extract_first()
            except:
                chpTitle = None
            # print('chp' + str(chpTitle))
            if not chpTitle is None:
                full += str(chpTitle) + "\n\n"
        # print(css)
        if text == []:
            return nums, ''
        full = full + "\n".join(text)
        full = full + "\n\n"
        return nums, full

    def direct(self, urls: t.List[str], novel: t.Dict[int, str], name: int) -> dict:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.easy, i, j, self.urlcss, self.chptitlecss) for i, j in enumerate(urls)]
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
        help='Crawls other sites for novels. Currently available trxs, tongrenquan, ffxs, bixiange, powanjuan, biqugeabc, uuks')
    async def crawl(self, ctx, link=None):
        if ctx.author.id in self.bot.crawler:
            return await ctx.reply("> **❌You cannot crawl two novels at the same time.**")
        allowed = self.bot.allowed
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
        soup = BeautifulSoup(await res.read(), 'html.parser')
        data = await res.read()
        soup1 = BeautifulSoup(data, 'lxml')
        self.titlecss = findchptitlecss(link)
        maintitleCSS = self.titlecss[0]
        try:
            title_name = str(soup1.select(maintitleCSS)[0].text)
        except:
            title = f"{ctx.author.id}_crawl"
        # print('titlename'+title_name)
        self.chptitlecss = self.titlecss[1]
        if title_name == '' or title_name == 'None' or title_name is None :
            title = f"{ctx.author.id}_crawl"
        else:
            title_name = GoogleTranslator(source='auto', target='english').translate(title_name)
            title = str(title_name)
        self.urlcss = findURLCSS(link)
        # print('translated' + title_name)
        # print(self.urlcss)
        name = str(link.split('/')[-1].replace('.html', ''))
        frontend_part = link.replace(f'/{name}', '').split('/')[-1]
        frontend = link.replace(f'/{name}', '').replace(f'/{frontend_part}', '')
        urls = [f'{frontend}{j}' for j in [str(i.get('href')) for i in soup.find_all('a')] if
                name in j and '.html' in j and 'txt' not in j]
        if urls == []:
            if 'sj.uukanshu' in link:
                surl = '/sj.uukanshu.com/'
                urls = [f'{frontend}{surl}{j}' for j in [str(i.get('href')) for i in soup.find_all('a')] if
                        'read.aspx?tid' in j and 'txt' not in j]
            else:
                urls = [f'{frontend}{j}' for j in [str(i.get('href')) for i in soup.find_all('a')] if
                        name in j and 'txt' not in j]
        self.bot.crawler[ctx.author.id] = f'0/{len(urls)}'
        await ctx.reply(f"> **✔Crawl started.**")
        book = await self.bot.loop.run_in_executor(None, self.direct, urls, novel, ctx.author.id)
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
            except Exception as e:
                print(e)
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
