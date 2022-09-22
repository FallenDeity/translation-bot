import asyncio
import concurrent.futures
import itertools
import os
import random
import typing
import typing as t
from urllib.parse import urljoin
from urllib.parse import urlparse

import aiofiles
import discord
import parsel
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from discord.ext import commands
from readabilipy import simple_json_from_html_string

from cogs.library import Library
from core.bot import Raizel
from utils.handler import FileHandler

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
    elif "readwn" in link:
        return ".chapter-content"
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
        if response.status_code == 404:
            return nums, ""
        response.encoding = response.apparent_encoding
        full = ""
        if '* ::text' == css or css is None or css.strip() == '':
            try:
                article = simple_json_from_html_string(response.text)
                text = article['plain_text']
                chpTitle = article['title']
                # print(chpTitle)
                full += str(chpTitle) + "\n\n"
                for i in text:
                    full += i['text'] + "\n"
            except:
                full = ""

        if full == "":
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

    async def getcontent(self, links: str, css: str, next_xpath, bot, tag):
        try:
            response = await bot.con.get(links)
            soup = BeautifulSoup(await response.read(), "html.parser", from_encoding=response.get_encoding())
            # response = requests.get(links, headers=headers, timeout=10)
        except:
            return ['error', links]
        if response.status == 404:
            return ['error', links]

        # response.encoding = response.apparent_encoding
        # chp_html = response.text
        sel = parsel.Selector(str(soup))
        article = simple_json_from_html_string(str(soup))
        chpTitle = article['title']
        full_chp = ""
        if '* ::text' == css or css is None or css.strip() == '':
            text = article['plain_text']
            full_chp += str(chpTitle) + "\n\n"
            for i in text:
                full_chp += i['text'] + "\n"
        else:
            full_chp += str(chpTitle) + "\n\n"
            text = sel.css(css).extract()
            # print(css)
            if text == []:
                return ""
            full_chp = full_chp + "\n".join(text)
        try:
            if tag:
                raise Exception
            next_href = sel.xpath(next_xpath + '/@href').extract()[0]
            next_href = urljoin(links, next_href)
        except:
            try:
                # if css selector is given it will come here due to exception
                next_href = sel.css(next_xpath).extract_first()
                next_href = urljoin(links, next_href)
            except:
                next_href = None

        full_chp = full_chp + "\n---------------------xxx---------------------\n"

        return [full_chp, next_href]

    def xpath_soup(self, element):
        components = []
        child = element if element.name else element.parent
        for parent in child.parents:
            previous = itertools.islice(parent.children, 0, parent.contents.index(child))
            xpath_tag = child.name
            xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
            components.append(xpath_tag if xpath_index == 1 else '%s[%d]' % (xpath_tag, xpath_index))
            child = parent
        components.reverse()
        return '/%s' % '/'.join(components)

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
        msg = await ctx.reply('Started crawling please wait')
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
        if link[-1] == "/" and "69shu" not in link and "uukanshu.cc" not in link and not num == len(allowed):
            link = link[:-1]
        if "m.uuks" in link:
            link = link.replace("m.", "")
        await ctx.typing()
        try:
            res = await self.bot.con.get(link)
        except Exception as e:
            print(e)
            await msg.delete()
            return await ctx.send("We couldn't connect to the provided link. Please check the link")
        novel = {}
        soup = BeautifulSoup(await res.read(), "html.parser", from_encoding=res.get_encoding())
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
            host = urlparse(link).netloc
            if urls == [] or len(urls) < 30:
                urls = [
                    f"{j}"
                    for j in [str(i.get("href")) for i in soup.find_all("a")]
                    if "txt" not in j
                ]
            utemp = []
            for url in urls:
                utemp.append(urljoin(link, url))
            urls = [u for u in utemp if host in u]
        if urls == [] or len(urls) < 30:
            if link[-1] == '/':
                link = link[:-1]

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
            host = urlparse(link).netloc
            if urls == [] or len(urls) < 30:
                urls = [
                    f"{j}"
                    for j in sel.css('a ::attr(href)').extract()
                    if "txt" not in j
                ]

            utemp = []
            for url in urls:
                utemp.append(urljoin(link, url))
            urls = [u for u in utemp if host in u]
            # print(urls)
            title_name = sel.css(maintitleCSS + " ::text").extract_first()
            # print(urls)
        if len(urls) < 30:
            return await ctx.reply(
                f"> **❌Currently this link is not supported.**"
            )
        if 'b.faloo' in link or 'wap.faloo' in link:
            urls = urls[:200]
        if reverse is not None:
            urls.reverse()
        for tag in ['/', '\\', '!', '<', '>', "'", '"', ':', ";", '?', '|', '*', ';', '\r', '\n', '\t', '\\\\']:
            title_name = title_name.replace(tag, '')
        title_name = title_name.replace('_', ' ')
        if title_name in self.bot.titles:
            novel_data = list(await self.bot.mongo.library.get_novel_by_name(name))
            ids = []
            for n in novel_data:
                ids.append(n._id)
            if True:
                chk_msg = await ctx.send(embed=discord.Embed(description=f"This novel is already in our library...  Do you want to search in library ...react with in this message 🇾  ...\n If you want to continue crawling react with 🇳"))
                await chk_msg.add_reaction('🇾')
                await chk_msg.add_reaction('🇳')

                def check(reaction, user):
                    return reaction.message.id == chk_msg.id and (str(reaction.emoji) == '🇾' or str(reaction.emoji) == '🇳') and user == ctx.author
                try:
                    res = await self.bot.wait_for(
                        "reaction_add",
                        check=check,
                        timeout=10.0,
                    )
                except asyncio.TimeoutError:
                    print(' Timeout error')
                    try:
                        os.remove(f"{ctx.author.id}.txt")
                    except:
                        pass
                    await ctx.send("No response detected. sending novels in library", delete_after=10)
                    ctx.command = await self.bot.get_command("library search").callback(Library(self.bot), ctx, title_name)
                    return None
                else:
                    await ctx.send("Reaction received", delete_after=10)
                    if str(res[0]) == '🇳':
                        await chk_msg.delete()
                        pass
                    else:
                        try:
                            os.remove(f"{ctx.author.id}.txt")
                        except:
                            pass
                        ctx.command = await self.bot.get_command("library search").callback(Library(self.bot), ctx, title_name)
                        return None
        try:
            self.bot.crawler[ctx.author.id] = f"0/{len(urls)}"
            await msg.edit(content="> **✔Crawl started.**")
            book = await self.bot.loop.run_in_executor(
                None, self.direct, urls, novel, ctx.author.id
            )
            parsed = {k: v for k, v in sorted(book.items(), key=lambda item: item[0])}
            whole = [i for i in list(parsed.values())]
            whole.insert(0, "\nsource : " + str(link) + "\n\n")
            text = "\n".join(whole)
            original_Language = FileHandler.find_language(text)
            if title_name == "" or title_name == "None" or title_name is None:
                title = f"{ctx.author.id}_crl"
                title_name = link
            else:
                if original_Language == 'english':
                    title = str(title_name[:100])
                else:
                    try:
                        title = GoogleTranslator(
                            source="auto", target="english"
                        ).translate(title_name).strip()
                    except:
                        pass
                    title_name = title + "__" + title_name
                    title = str(title[:100])

            async with aiofiles.open(f"{title}.txt", "w", encoding="utf-8") as f:
                await f.write(text)
            await FileHandler().crawlnsend(ctx, self.bot, title, title_name, original_Language)
        except Exception as e:
            await ctx.send("> Error occurred .Please report to admin +\n" + str(e))
            raise e
        finally:
            del self.bot.crawler[ctx.author.id]
            self.bot.titles = await self.mongo.library.get_all_titles
            self.bot.titles = random.sample(self.bot.titles, len(self.bot.titles))

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

    @commands.hybrid_command(
        help="Crawls if given 1st,2nd(or selector) and lastpage(or maxchps).use it when there is no TOC page")
    async def crawlnext(
            self, ctx: commands.Context, firstchplink: str, secondchplink: str = None, lastchplink: str = None,
            nextselector: str = None, noofchapters: int = None,
            cssselector: str = None
    ) -> typing.Optional[discord.Message]:
        if ctx.author.id in self.bot.crawler:
            return await ctx.reply(
                "> **❌You cannot crawl two novels at the same time.**"
            )
        if secondchplink is None and nextselector is None:
            return await ctx.send("You must give second chapter link or next page css selector")
        msg = await ctx.send("Crawling will be started soon")
        if cssselector:
            css = cssselector
            if '::text' not in css:
                css += ' ::text'
        else:
            css = '* ::text'
        if noofchapters is None:
            noofchapters = 2000
        try:
            response = requests.get(firstchplink, headers=headers, timeout=10)
        except:
            return await ctx.reply("> Couldn't connect to the provided link.... Please check the link")
        if response.status_code == 404:
            return await ctx.reply("> Provided link gives 404 error... Please check the link")
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.content, 'html5lib')
        htm = response.text
        sel = parsel.Selector(htm)
        sel_tag = False
        if nextselector is not None:

            sel_tag = True
            if '::attr(href)' not in nextselector:
                nextselector += ' ::attr(href)'
            print(nextselector)
            path = nextselector
        else:

            urls = sel.css('a ::attr(href)').extract()

            psrt = ''
            for url in urls:
                full_url = urljoin(firstchplink, url)
                if full_url == secondchplink:
                    psrt = url
            if psrt == '':
                await msg.delete()
                return await ctx.send(
                    "We couldn't find the selector for next chapter. Please check the links or provide the css selector")
            href = [i for i in soup.find_all("a") if i.get("href") == psrt]
            # print(href)
            path = self.xpath_soup(href[0])
        title = sel.css('title ::text').extract_first()
        chp_count = 1
        # print(title)
        current_link = firstchplink
        full_text = "Source : " + firstchplink + '\n\n'
        no_of_tries = 0
        await msg.edit(content="> Crawling started")
        crawled_urls = []
        try:
            for i in range(1, noofchapters):
                self.bot.crawler[ctx.author.id] = f"{i}/{noofchapters}"
                if current_link in crawled_urls:
                    await msg.delete()
                    if i >= 30:
                        break
                    del self.bot.crawler[ctx.author.id]
                    if current_link == firstchplink and i < 10:
                        return await ctx.reply(
                            'Error occurred . Some problem in the site. please try with second and third chapter or give valid css selector for next page button')
                    if sel_tag:
                        return await ctx.send(" There is some problem with the provided selector")
                    else:
                        return await ctx.send(" There is some problem with the detected selector")
                output = await self.getcontent(current_link, css, path, self.bot, sel_tag)
                chp_text = output[0]
                # print(i)
                if chp_text == 'error':
                    no_of_tries += 1
                    chp_text = ''
                    if no_of_tries > 30:
                        await msg.delete()
                        del self.bot.crawler[ctx.author.id]
                        return await ctx.send('Error occured when crawling. Please Report to my developer')
                full_text += chp_text
                # print(current_link)
                if current_link == lastchplink or i >= noofchapters or output[1] is None:
                    print('break')
                    break
                chp_count += 1
                current_link = output[1]
            original_Language = FileHandler.find_language(full_text)
            if title is None or str(title).strip() == "" or title == "None":
                title = f"{ctx.author.id}_crl"
                title_name = firstchplink
            else:
                title_name = title
                if original_Language == 'english':
                    title = str(title[:100])
                else:
                    try:
                        title = GoogleTranslator(
                            source="auto", target="english"
                        ).translate(title).strip()
                    except:
                        pass
                    title_name = title + "__" + title_name
                    try:
                        title = str(title[:100])
                    except:
                        pass
                for tag in ['/', '\\', '<', '>', "'", '"', ':', ";", '?', '|', '*', ';', '\r', '\n', '\t', '\\\\']:
                    title = title.replace(tag, '')
            with open(title + '.txt', 'w', encoding='utf-8') as f:
                f.write(full_text)
            return await FileHandler().crawlnsend(ctx, self.bot, title, title_name, original_Language)
        except Exception as e:
            await ctx.send("> Error occurred .Please report to admin +\n"+str(e))
            raise e
        finally:
            del self.bot.crawler[ctx.author.id]


async def setup(bot: Raizel) -> None:
    await bot.add_cog(Crawler(bot))
