import re
import sys
import typing as t
from concurrent.futures import ThreadPoolExecutor, as_completed

import cloudscraper
import trafilatura
from bs4 import BeautifulSoup

from src.assets import ValidSites

from .base_session import BaseSession

if t.TYPE_CHECKING:
    from src import TranslationBot


__all__: tuple[str, ...] = ("Scraper",)
sys.setrecursionlimit(10000)


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    " (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}


class Scraper(BaseSession):
    soup: BeautifulSoup

    def __init__(self, *, bot: "TranslationBot", link: str) -> None:
        self.bot = bot
        self.scraper = cloudscraper.create_scraper()
        self.link = link
        self.scraper.headers.update(HEADERS)
        self.pages: list[BeautifulSoup] = []
        super().__init__(bot=bot)

    @staticmethod
    def _get_title(soup: BeautifulSoup) -> str:
        for tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            try:
                if title := soup.select_one(tag):
                    return title.get_text().strip()
            except Exception:
                pass
        return ""

    def tokenize(self) -> tuple[str, ...]:
        url = self.link.rstrip(".html").rstrip(".htm/")
        suffix = url.split("/")[-1]
        midfix = url.replace(f"/{suffix}", "").split("/")[-1]
        prefix = url.replace(f"/{midfix}/{suffix}", "")
        return url, suffix, midfix, prefix

    def get_thumbnail(self) -> str:
        response = self.scraper.get(self.link)
        soup = BeautifulSoup(response.content, "lxml")
        url, suffix, midfix, prefix = self.tokenize()
        compound = (
            ValidSites.READWN,
            ValidSites.FANNOVELS,
            ValidSites.NOVELMT,
            ValidSites.WUXIAX,
        )
        imgs = []
        tag = "src" if not any(str(i.value) in self.link for i in compound) else "data-src"
        for img in soup.find_all("img"):
            if any(x in img.get(tag, "") for x in ("cover", "thumb", ".jpg", "upload")) and ".png" not in img.get(
                tag, ""
            ):
                imgs.append(img.get(tag, ""))
        if imgs:
            img = imgs[0]
            for i in imgs:
                if suffix in i or "/file" in i or midfix in i:
                    if str(ValidSites.NOVELSKNIGHT.value) in self.link:
                        img = i if "resize=" in i.get("src", "") else img
                        break
                    img = i
                    break
            if "http" not in img:
                domain = x.group() if (x := re.search(r"(?<=//)[^/]+", url)) else ""
                status = "https" if "https" in url else "http"
                img = f"{status}://{domain}{img}"
                if self.scraper.get(img).status_code != 200:
                    img = img.lstrip(f"{status}://{domain}")
                    return f"{prefix}{img}"
            return img
        meta = soup.find_all("meta")
        for i in meta:
            if i.get("property") == "og:image":
                return i.get("content", "")
        return ""

    def get_description(self) -> str:
        aliases = ("description", "Description", "DESCRIPTION", "desc", "Desc", "DESC")
        description = ""
        for meta in self.soup.find_all("meta"):
            if meta.get("name") in aliases:
                description += meta.get("content")
        return description

    async def get_title_from_link(self, link: str) -> str:
        response = await self.bot.loop.run_in_executor(None, self.scraper.get, link)
        data = response.text if any(str(i.value) in self.link for i in (ValidSites.BIQUGEABC,)) else response.content
        soup = BeautifulSoup(data, "lxml")
        return self._get_title(soup)

    async def is_valid(self) -> bool:
        response = await self.bot.loop.run_in_executor(None, self.scraper.get, self.link)
        if response.status_code == 200:
            return True
        if response.status_code == 404:
            self.link = self.link + "/"
            response = await self.bot.loop.run_in_executor(None, self.scraper.get, self.link)
            return response.status_code == 200
        return False

    async def get_soup(self) -> BeautifulSoup:
        response = await self.bot.loop.run_in_executor(None, self.scraper.get, self.link)
        data = response.text if any(str(i.value) in self.link for i in (ValidSites.BIQUGEABC,)) else response.content
        self.soup = BeautifulSoup(data, "lxml")
        await self.get_link()
        await self.get_pages()
        return self.soup

    async def get_link(self) -> None:
        if str(ValidSites.TXT520.value) in self.link and "-" not in self.link:
            for link in self.soup.find_all("a"):
                if "read/" in str(link.get("href")) and self.link.split("/")[-1].rstrip(".html") in str(
                    link.get("href")
                ):
                    self.link = f"https://www.txt520.com{link.get('href')}"
                    response = await self.bot.loop.run_in_executor(None, self.scraper.get, self.link)
                    self.soup = BeautifulSoup(response.content, "lxml")
                    break

    async def get_pages(self) -> list[BeautifulSoup]:
        url, suffix, midfix, prefix = self.tokenize()
        done: list[str] = []
        if f"sj.{ValidSites.UUKANSHU.value}" in self.link:
            for link in self.soup.find_all("a"):
                if (
                    f"{suffix}" in str(link.get("href"))
                    and "page=" in str(link.get("href"))
                    and str(link.get("href")) not in done
                ):
                    url = f"{prefix}/{midfix}/{link['href']}"
                    response = await self.bot.loop.run_in_executor(None, self.scraper.get, url)
                    self.pages.append(BeautifulSoup(response.content, "lxml"))
                    done.append(str(link.get("href")))
        elif str(ValidSites.NOVELFULL.value) in self.link:
            nums: list[int] = []
            for link in self.soup.find_all("a"):
                if f"{suffix}" in str(link.get("href")) and "page=" in str(link.get("href")):
                    nums.append(int(str(link.get("href")).split("=")[-1]))
            max_page = max(nums)
            links = [f"{prefix}/{midfix}/{suffix}.html?page={i}" for i in range(1, max_page + 1)]
            for link in links:
                response = await self.bot.loop.run_in_executor(None, self.scraper.get, link)
                self.pages.append(BeautifulSoup(response.content, "lxml"))
        elif str(ValidSites.MXINDINGDIANXSW.value) in self.link:
            links = list(
                dict.fromkeys(
                    [
                        f"{prefix}{a.get('href')}"
                        for a in self.soup.find_all("a")
                        if f"/{suffix}/" in str(a.get("href")) and "index" not in str(a.get("href"))
                    ]
                )
            )
            links = await self.bot.loop.run_in_executor(
                None,
                self._bucket_paginator,
                prefix,
                links[-1],
                (
                    "下一页",
                    "下一章",
                ),
            )
            soup = BeautifulSoup("", "lxml")
            for link in links:
                soup.append(BeautifulSoup(f'<a href="{link}"></a>', "lxml"))
            self.soup = soup
        elif str(ValidSites.SOXSCC.value) in url:
            links = list(
                dict.fromkeys(
                    [
                        f"{prefix}{a.get('href')}"
                        for a in self.soup.find_all("a")
                        if f"/{suffix}/" in str(a.get("href"))
                        and "index" not in str(a.get("href"))
                        and ".html" in str(a.get("href"))
                    ]
                )
            )
            links = await self.bot.loop.run_in_executor(
                None,
                self._bucket_paginator,
                prefix,
                links[-1],
                (
                    "下一页",
                    "下一章",
                ),
            )
            soup = BeautifulSoup("", "lxml")
            for link in links:
                soup.append(BeautifulSoup(f'<a href="{link}"></a>', "lxml"))
            self.soup = soup
        return self.pages

    def get_title(self, css: tuple[str, ...]) -> str:
        for tag in css:
            try:
                if title := self.soup.select_one(tag):
                    return title.get_text().strip()
            except Exception:
                pass
        return ""

    def _get_next_link(self, n: int, prefix: str, link: str, data: dict[int, str], selectors: tuple[str, ...]) -> None:
        resp = self.scraper.get(link)
        soup = BeautifulSoup(resp.content, "lxml")
        for a in soup.find_all("a"):
            if any(selector in a.get_text() for selector in selectors):
                data[n] = f"{a.get('href')}"
                self.bot.logger.info(f"Found next link: {data[n]} [{len(data)}]")
                return self._get_next_link(n + 1, prefix, f"{prefix}{data[n]}", data, selectors)
        return None

    def _bucket_paginator(self, prefix: str, link: str, selelctors: tuple[str, ...]) -> list[str]:
        data: dict[int, str] = {1: link}
        self._get_next_link(len(data) + 1, prefix, link, data, selelctors)
        return list(data.values())

    def _scrape(self, link: str, n: int, data: dict[int, str]) -> None:
        response = self.scraper.get(link)
        soup = BeautifulSoup(response.content, "lxml")
        text = trafilatura.extract(response.content)
        title = self._get_title(soup)
        data[n] = f"\n{title}\n\n{text}\n"

    def bucket_scrape(self, links: list[str], progress: dict[int, str], user_id: int) -> str:
        data: dict[int, str] = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self._scrape, link, n, data) for n, link in enumerate(links)]
            for _ in as_completed(futures):
                progress[user_id] = f"Crawling {round((len(data) / len(links)) * 100)}%"
                self.bot.logger.info(f"Crawling {round((len(data) / len(links)) * 100)}% for {user_id}")
        ordered = [text for _, text in sorted(data.items(), key=lambda item: item[0])]
        return "\n\n\n".join(ordered)
