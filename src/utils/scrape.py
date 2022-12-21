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

    async def get_title_from_link(self, link: str) -> str:
        response = await self.bot.loop.run_in_executor(None, self.scraper.get, link)
        soup = BeautifulSoup(response.content, "html.parser")
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
        self.soup = BeautifulSoup(response.content, "html.parser")
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
                    self.soup = BeautifulSoup(response.content, "html.parser")
                    break

    async def get_pages(self) -> list[BeautifulSoup]:
        url = self.link.rstrip(".html").rstrip(".htm/")
        suffix = url.split("/")[-1]
        midfix = url.replace(f"/{suffix}", "").split("/")[-1]
        prefix = url.replace(f"/{midfix}/{suffix}", "")
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
                    self.pages.append(BeautifulSoup(response.content, "html.parser"))
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
                self.pages.append(BeautifulSoup(response.content, "html.parser"))
        return self.pages

    def get_title(self, css: tuple[str, ...]) -> str:
        for tag in css:
            try:
                if title := self.soup.select_one(tag):
                    return title.get_text().strip()
            except Exception:
                pass
        return ""

    def _scrape(self, link: str, n: int, data: dict[int, str]) -> None:
        response = self.scraper.get(link)
        soup = BeautifulSoup(response.content, "html.parser")
        text = trafilatura.extract(response.content)
        title = self._get_title(soup)
        data[n] = f"{title}\n\n{text}"

    def bucket_scrape(self, links: list[str], progress: dict[int, str], user_id: int) -> str:
        data: dict[int, str] = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self._scrape, link, n, data) for n, link in enumerate(links)]
            for _ in as_completed(futures):
                progress[user_id] = f"Crawling {round((len(data) / len(links)) * 100)}%"
                self.bot.logger.info(f"Crawling {round((len(data) / len(links)) * 100)}% for {user_id}")
        ordered = [text for _, text in sorted(data.items(), key=lambda item: item[0])]
        return "\n\n".join(ordered)
