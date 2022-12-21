import typing as t

import disnake
import trafilatura
from disnake.ext import commands

from src.assets import Languages, Sites, ValidSites
from src.utils import Scraper, Translator

from . import Cog

if t.TYPE_CHECKING:
    from .translator import Translate


class Crawl(Cog):
    crawler_tasks: dict[int, str] = {}

    async def cog_before_slash_command_invoke(self, inter: disnake.ApplicationCommandInteraction) -> None:
        if await self.bot.mongo.warns.blocked(inter.user.id):
            await inter.response.send_message("You have been blocked from using this bot")
            raise commands.CheckFailure(f"{inter.user} is blocked from using this bot")

    @commands.slash_command(name="crawl", description="Crawl a website")
    async def crawl(self, ctx: disnake.ApplicationCommandInteraction) -> None:
        ...

    @crawl.sub_command(name="crawl", description="Crawl a website")
    @commands.max_concurrency(1, commands.BucketType.user)
    async def crawl_(
        self,
        inter: disnake.ApplicationCommandInteraction,
        url: str,
        translate: bool = False,
        translate_to: str = "en",
        term: bool = False,
    ) -> None:
        """Crawl a website

        Parameters
        ----------
        inter : disnake.ApplicationCommandInteraction
            The interaction
        url : str
            The url to crawl
        translate : bool, optional
            Whether to translate the text, by default False
        translate_to : str, optional
            The language to translate to, by default "en"
        term : bool, optional
            Whether to term the text, by default False
        """
        if not ValidSites.is_valid(url):
            raise commands.BadArgument("This website is not supported")
        if translate_to not in Languages.all_languages():
            raise commands.BadArgument("Invalid language")
        if term and term not in self.bot.termer.get_categories():
            raise commands.BadArgument("Invalid term")
        await inter.send("> **Crawling...**")
        link = ValidSites.format_link(url)
        crawler = Scraper(bot=self.bot, link=link)
        translator = Translator(bot=self.bot, target=translate_to)
        if not await crawler.is_valid():
            raise commands.BadArgument("This website is not supported")
        await crawler.get_soup()
        title = crawler.get_title(Sites.title_css_from_link(crawler.link))
        title = await crawler.get_title_from_link(url) if not title else title
        title = await translator.translate(title) if title else f"{inter.user.id}_{url}"
        title = await translator.format_name(title)
        await inter.edit_original_response(content=f"> **Crawling...**\n> **Title:** {title}")
        urls = ValidSites.get_urls(crawler.soup, crawler.link) + sum(
            [ValidSites.get_urls(i, crawler.link) for i in crawler.pages], []
        )
        if not urls:
            raise commands.BadArgument("No chapters found")
        text = await self.bot.loop.run_in_executor(None, crawler.scraper.get, urls[0])
        text = trafilatura.extract(text.content)
        language = await translator.detect(text)
        if not await crawler.check_library(inter, language, title):
            return
        await inter.edit_original_response(
            content=f"> **Crawling...**\n> **Title:** {title}\n> **Language:** {language}"
        )
        text = await self.bot.loop.run_in_executor(None, crawler.bucket_scrape, urls, self.crawler_tasks, inter.user.id)
        if translate:
            if language != Languages.from_string(translate_to):
                await inter.edit_original_response(content="> **Translating...**")
                cog: "Translate" = t.cast("Translate", self.bot.get_cog("Translate"))
                text = await self.bot.loop.run_in_executor(
                    None, translator.bucket_translate, text, cog.translator_tasks, inter.user.id, translate_to
                )
                await inter.edit_original_response(content=f"> **Translated to:** {translate_to}")
                cog.translator_tasks.pop(inter.user.id)
            await inter.edit_original_response(content="> **Not translating since the language is the same**")
        if term:
            await inter.edit_original_response(content="> **Filtering...**")
            text = self.bot.termer.replace_terms(text, term)
            await inter.edit_original_response(content=f"> **Filtered by:** {term}")
        await inter.edit_original_response(content="> **Uploading...**")
        await crawler.distribute_translations(inter, translator, text, translate_to, language, title, term, True)
        self.crawler_tasks.pop(inter.user.id)

    @crawl_.autocomplete("translate_to")
    async def crawl_language_autocomplete(
            self, _inter: disnake.ApplicationCommandInteraction, language: str
    ) -> dict[str, str]:
        """Autocomplete for the language parameter."""
        data: list[tuple[str, str]] = [
                                          (str(lang.name), str(lang.value)) for lang in Languages if
                                          lang.name.lower().startswith(language.lower())
                                      ][0:25]
        return {key: value for key, value in data}

    @crawl_.autocomplete("term")
    async def crawl_term_autocomplete(self, _inter: disnake.ApplicationCommandInteraction, term_: str) -> list[str]:
        """Autocomplete for the term parameter."""
        return [term for term in self.bot.termer.get_categories() if term.lower().startswith(term_.lower())][0:25]

    @crawl.sub_command(name="progress", description="Check the progress of a crawl")
    async def progress(self, inter: disnake.ApplicationCommandInteraction) -> None:
        if inter.user.id not in self.crawler_tasks:
            raise commands.BadArgument("You have no active crawls")
        await inter.send(f"> **Progress:** {self.crawler_tasks[inter.user.id]}")

    @commands.message_command(name="multi-crawl", description="Crawl multiple websites")
    async def multi_crawl(self, inter: disnake.ApplicationCommandInteraction, message: disnake.Message) -> None:
        ...
