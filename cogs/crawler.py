import concurrent.futures
import os
import typing
import typing as t
import zipfile

import aiofiles
import discord
import parsel
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from discord.ext import commands
from readabilipy import simple_json_from_html_string

from core.bot import Raizel
from core.views.linkview import LinkView
from utils.handler import FileHandler
from urllib.parse import urljoin

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def findURLCSS(link):
    if "bixiange" in link:
        return "p ::text"
    elif "sj.uukanshu" in link or "t.uukanshu" in link:
        return "#read-page p ::text"
    elif "uukanshu.cc" in link:
        return ".bbb.font-normal.readcotent ::text"
    elif "uukanshu" in link:
        return ".contentbox ::text"
    elif (
        "trxs.me" in link
        or "trxs.cc" in link
        or "qbtr" in link
        or "tongrenquan" in link
    ):
        return ".read_chapterDetail p ::text"
    elif "biqugeabc" in link:
        return ".text_row_txt >p ::text"
    elif "uuks" in link:
        return "div#contentbox > p ::text"
    elif "jpxs" in link:
        return ".read_chapterDetail p ::text"
    elif "powanjuan" in link or "ffxs" in link or "sjks" in link:
        return ".content p::text"
    elif "69shu" in link:
        return ".txtnav ::text"
    elif "ptwxz" in link:
        return "* ::text"
    elif "shu05" in link:
        return "#htmlContent ::text"
    else:
        return "* ::text"


def findchptitlecss(link):
    if (
        "trxs.me" in link
        or "trxs.cc" in link
        or "tongrenquan" in link
        or "qbtr" in link
        or "jpxs" in link
    ):
        return [".infos>h1:first-child", ""]
    if "bixiange" in link:
        return [".desc>h1", ""]
    if "powanjuan" in link or "ffxs" in link:
        return ["title", ""]
    if "sjks" in link:
        return [".box-artic>h1", ""]
    if "sj.uukanshu" in link or "t.uukanshu" in link:
        return [".bookname", "#divContent >h3 ::text"]
    if "uukanshu.cc" in link:
        return [".booktitle", "h1 ::text"]
    if "biqugeabc" in link:
        return ["title", "title ::text"]
    if "uuks" in link:
        return [".jieshao_content>h1", "h1#timu ::text"]
    if "uukanshu" in link:
        return ["title", "h1#timu ::text"]
    if "69shu" in link:
        return [".bread>a:nth-of-type(3)", "title ::text"]
    if "ptwxz" in link:
        return [".title", "title ::text"]
    else:
        return ["title", "title ::text"]


class Crawler(commands.Cog):
    def __init__(self, bot: Raizel) -> None:
        self.titlecss = None
        self.chptitlecss = None
        self.urlcss = None
        self.bot = bot

    @staticmethod
    def easy(nums: int, links: str, css: str, chptitleCSS) -> t.Tuple[int, str]:
        response = None
        try:
            response = requests.get(links, headers=headers, timeout=10)
        except:
            return nums, f"\ncouldn't get connection to {links}\n"
        response.encoding = response.apparent_encoding
        full = ""
        if '* ::text' == css or css is None or css.strip() == '':
            article = simple_json_from_html_string(response.text)
            text = article['plain_text']
            chpTitle = article['title']
            # print(chpTitle)
            full += str(chpTitle) + "\n\n"
            for i in text:
                full += i['text'] + "\n"

        else:
            html = response.text
            sel = parsel.Selector(html)
            text = sel.css(css).extract()

            if not chptitleCSS == "":
                try:
                    chpTitle = sel.css(chptitleCSS).extract_first()
                except:
                    chpTitle = None
                # print('chp' + str(chpTitle))
                if not chpTitle is None:
                    full += str(chpTitle) + "\n\n"
            # print(css)
            if text == []:
                return nums, ""
            if "ptwxz" in links:
                while text[0] != "GetFont();":
                    text.pop(0)
                text.pop(0)
            full = full + "\n".join(text)
        full = full + "\n---------------------xxx---------------------\n"
        return nums, full

    def direct(self, urls: t.List[str], novel: t.Dict[int, str], name: int) -> dict:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(self.easy, i, j, self.urlcss, self.chptitlecss)
                for i, j in enumerate(urls)
            ]
            for future in concurrent.futures.as_completed(futures):
                novel[future.result()[0]] = future.result()[1]
                self.bot.crawler[name] = f"{len(novel)}/{len(urls)}"
            return novel

    @commands.hybrid_command(help="Gives progress of novel crawling", aliases=["cp"])
    async def crawled(self, ctx: commands.Context) -> typing.Optional[discord.Message]:
        if ctx.author.id not in self.bot.crawler:
            return await ctx.send(
                "> **❌You have no novel deposited for crawling currently.**"
            )
        await ctx.send(f"> **🚄`{self.bot.crawler[ctx.author.id]}`**")

    @commands.hybrid_command(
        help="Crawls other sites for novels. \nselector: give the css selector for the content page. It will try to auto select if not given\n Reverse: give any value if Table of Content is reversed in the given link(or if crawled novel needs to be reversed)")
    async def crawl(
            self, ctx: commands.Context, link: str = None, reverse: str = None, selector: str = None
    ) -> typing.Optional[discord.Message]:
        if ctx.author.id in self.bot.crawler:
            return await ctx.reply(
                "> **❌You cannot crawl two novels at the same time.**"
            )
        allowed = self.bot.allowed
        if link is None:
            return await ctx.reply(f"> **❌Enter a link for crawling.**")
        await ctx.send('Started crawling please wait', delete_after=10)
        num = 0
        for i in allowed:
            if i not in link:
                num += 1
        # if num == len(allowed):
        #     return await ctx.reply(
        #         f"> **❌We currently crawl only from {', '.join(allowed)}**"
        #     )
        if "69shu" in link and "txt" in link:
            link = link.replace("/txt", "")
            link = link.replace(".htm", "/")
        if "ptwxz" in link and "bookinfo" in link:
            link = link.replace("bookinfo", "html")
            link = link.replace(".html", "/")
        if link[-1] == "/" and "69shu" not in link and "uukanshu.cc" not in link:
            link = link[:-1]
        if "m.uuks" in link:
            link = link.replace("m.", "")
        await ctx.typing()
        res = await self.bot.con.get(link)
        novel = {}
        soup = BeautifulSoup(await res.read(), "html.parser")
        data = await res.read()
        soup1 = BeautifulSoup(data, "lxml")
        self.titlecss = findchptitlecss(link)
        maintitleCSS = self.titlecss[0]
        try:
            title_name = str(soup1.select(maintitleCSS)[0].text)
            if title_name == "" or title_name is None:
                raise Exception
        except Exception as e:
            print(e)
            try:
                title_name = ""
                response = requests.get(link, headers=headers)
                response.encoding = response.apparent_encoding
                html = response.text
                sel = parsel.Selector(html)
                try:
                    title_name = sel.css(maintitleCSS + " ::text").extract_first()
                except Exception as e:
                    print("error at 200" + str(e))
                if title_name.strip() == "" or title_name is None:
                    title_name = sel.css("title ::text").extract_first()
                # print(title)

            except Exception as ex:
                print(ex)
                title_name = f"{ctx.author.id}_crl"
        # print('titlename'+title_name)
        self.chptitlecss = self.titlecss[1]

        if selector is None:
            self.urlcss = findURLCSS(link)
        else:
            if not '::text' in selector:
                selector = selector + " ::text"
            self.urlcss = selector
        # print('translated' + title_name)
        # print(self.urlcss)
        name = str(link.split("/")[-1].replace(".html", ""))
        # name=name.replace('all','')
        urls = []
        frontend_part = link.replace(f"/{name}", "").split("/")[-1]
        frontend = link.replace(f"/{name}", "").replace(f"/{frontend_part}", "")
        if "69shu" in link:
            urls = [
                f"{j}"
                for j in [str(i.get("href")) for i in soup.find_all("a")]
                if name in j and "http" in j
            ]
        elif "ptwxz" in link:
            frontend = link + "/"
            urls = [
                f"{frontend}{j}"
                for j in [str(i.get("href")) for i in soup.find_all("a")]
                if "html" in j
                   and "txt" not in j
                   and "http" not in j
                   and "javascript" not in j
                   and "modules" not in j
            ]
        elif "uukanshu.cc" in link:
            frontend = "https://uukanshu.cc/"
            urls = [
                f"{frontend}{j}"
                for j in [str(i.get("href")) for i in soup.find_all("a")]
                if "/book" in j and name in j and "txt" not in j
            ]
        else:
            urls = [
                f"{frontend}{j}"
                for j in [str(i.get("href")) for i in soup.find_all("a")]
                if name in j and ".html" in j and "txt" not in j
            ]
        if urls == []:
            if "sj.uukanshu" in link:
                surl = "/sj.uukanshu.com/"
                urls = [
                    f"{frontend}{surl}{j}"
                    for j in [str(i.get("href")) for i in soup.find_all("a")]
                    if "read.aspx?tid" in j and "txt" not in j
                ]
            # elif "uuks" in link:
            #     # print(frontend)
            #     # name=name.replace('all','')
            #     # print(name)
            #     urls = [
            #         f"{frontend}{j}"
            #         for j in [str(i.get("href")) for i in soup.find_all("a")]
            #         if "/b/" in j and "txt" not in j
            #     ]
                # print(urls)
            elif "t.uukanshu" in link:
                surl = "/t.uukanshu.com/"
                urls = [
                    f"{frontend}{surl}{j}"
                    for j in [str(i.get("href")) for i in soup.find_all("a")]
                    if "read.aspx?tid" in j and "txt" not in j
                ]
        if (
            "uukanshu" in link
            and "sj.uukanshu" not in link
            and "t.uukanshu" not in link
            and "uukanshu.cc" not in link
            and not urls == []
        ):
            urls = urls[::-1]
        if urls == [] or num == len(allowed) or len(urls) < 30:
            urls = [
                f"{j}"
                for j in [str(i.get("href")) for i in soup.find_all("a")]
                if name in j and "txt" not in j
            ]
            utemp = []
            for url in urls:
                utemp.append(urljoin(link, url))
            urls = utemp
        if urls == [] or len(urls) < 30:
            link = link + '/'

            try:
                response = requests.get(link, headers=headers, timeout=10)
            except:
                print('error')
            response.encoding = response.apparent_encoding
            html = response.text
            sel = parsel.Selector(html)
            urls = [
                f"{j}"
                for j in sel.css('a ::attr(href)').extract()
                if name in j and "txt" not in j
            ]
            utemp = []
            for url in urls:
                utemp.append(urljoin(link, url))
            urls = utemp
            # print(urls)
            title_name = sel.css(maintitleCSS + " ::text").extract_first()
            # print(urls)
        if len(urls) < 30:
            return await ctx.reply(
                f"> **❌Currently this link is not supported.**"
            )
        if reverse is not None:
            urls.reverse()
        self.bot.crawler[ctx.author.id] = f"0/{len(urls)}"
        await ctx.reply(f"> **✔Crawl started.**")
        if title_name == "" or title_name == "None" or title_name is None:
            title_name = f"{ctx.author.id}_crl"
        else:
            try:
                title_name = GoogleTranslator(
                    source="auto", target="english"
                ).translate(title_name).strip()
            except:
                pass
        title = str(title_name[:100])
        for tag in ['/', '\\', '<', '>', "'", '"', ':', ";", '?', '|', '*', ';', '\r', '\n', '\t', '\\\\']:
            title = title.replace(tag, '')
        title = title.replace('_', ' ')
        book = await self.bot.loop.run_in_executor(
            None, self.direct, urls, novel, ctx.author.id
        )
        parsed = {k: v for k, v in sorted(book.items(), key=lambda item: item[0])}
        whole = [i for i in list(parsed.values())]
        whole.insert(0, "\nsource : " + str(link) + "\n\n")
        async with aiofiles.open(f"{title}.txt", "w", encoding="utf-8") as f:
            await f.write("\n".join(whole))
        await FileHandler().crawlnsend(ctx, self.bot, title, title_name)

    @commands.hybrid_command(
        help="Clears any stagnant novels which were deposited for crawling."
    )
    async def cclear(self, ctx: commands.Context):
        if ctx.author.id in self.bot.crawler:
            del self.bot.crawler[ctx.author.id]
        files = os.listdir()
        for i in files:
            if str(ctx.author.id) in str(i) and "crawl" in i:
                os.remove(i)
        await ctx.reply("> **✔Cleared all records.**")


async def setup(bot: Raizel) -> None:
    await bot.add_cog(Crawler(bot))
