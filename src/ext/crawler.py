import typing as t

import disnake
import psutil
import trafilatura
from disnake.ext import commands

from src.assets import AnsiBuilder, BackgroundColors, Colors, Languages, Sites, Styles, ValidSites
from src.utils import Scraper, Translator

from . import Cog

if t.TYPE_CHECKING:
    from .translator import Translate


class Crawl(Cog):
    crawler_tasks: dict[int, str] = {}

    async def cog_before_slash_command_invoke(self, inter: disnake.ApplicationCommandInteraction) -> None:
        if await self.bot.mongo.warns.blocked(inter.user.id):
            raise commands.CheckFailure(f"{inter.user} is blocked from using this bot")

    @commands.slash_command(name="crawl", description="Crawl a website")
    async def crawl(self, _inter: disnake.ApplicationCommandInteraction) -> None:
        if _inter.application_command.qualified_name == "crawl crawl":
            if psutil.virtual_memory().percent > 90:
                raise commands.CheckFailure("The bot is currently under heavy load")
            if _inter.user.id in self.crawler_tasks:
                raise commands.CheckFailure("You already have a crawl task running")
        await _inter.response.defer()

    @staticmethod
    def _build_embed(
        status: str,
        title: str,
        link: str,
        description: str,
        thumbnail: str,
        translate: bool,
        translate_to: str,
        term: str,
    ) -> disnake.Embed:
        embed = disnake.Embed(
            title=title,
            description=f"{AnsiBuilder.to_ansi(status, Colors.RED, Styles.BOLD, BackgroundColors.FIREFLY_DARK_BLUE)}\n"
            f"{AnsiBuilder.to_ansi(description, Colors.CYAN) if description else ''}",
            url=link,
            color=disnake.Colour.random(),
        )
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        if translate:
            embed.add_field(name="Translation Language", value=translate_to, inline=True)
        if term:
            embed.add_field(name="Terming Category", value=term, inline=True)
        return embed

    @crawl.sub_command(name="crawl", description="Crawl a website")
    @commands.max_concurrency(1, commands.BucketType.user)
    async def crawl_(
        self,
        inter: disnake.ApplicationCommandInteraction,
        url: str,
        translate: bool = False,
        translate_to: str = "en",
        term: str = "",
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
        term : str, optional
            Whether to term the text, by default ""
        """
        if not ValidSites.is_valid(url):
            raise commands.BadArgument("This website is not supported")
        if translate_to not in Languages.all_languages():
            raise commands.BadArgument("Invalid language")
        if term and term not in self.bot.termer.get_categories():
            raise commands.BadArgument("Invalid term")
        translator_cog: "Translate" = t.cast("Translate", self.bot.get_cog("Translate"))
        if translate and inter.user.id in translator_cog.translator_tasks:
            raise commands.CheckFailure("You already have a translation task running")
        link = ValidSites.format_link(url)
        crawler = Scraper(bot=self.bot, link=link)
        translator = Translator(bot=self.bot, target=translate_to)
        if not await crawler.is_valid():
            raise commands.BadArgument("This website is not supported")
        await crawler.get_soup()
        description = await translator.translate(crawler.get_description(), target=Languages.English.value)
        thumbnail = await self.bot.loop.run_in_executor(None, crawler.get_thumbnail)
        title = crawler.get_title(Sites.title_css_from_link(crawler.link))
        title = await crawler.get_title_from_link(url) if not title else title
        title = await translator.translate(title) if title else f"{inter.user.id}_{url}"
        title = await translator.format_name(title)
        args = (
            title,
            link,
            description,
            thumbnail,
            translate,
            translate_to,
            term,
        )
        await inter.edit_original_response(embed=self._build_embed("Crawling currently", *args))
        urls = ValidSites.get_urls(crawler.soup, crawler.link) + sum(
            [ValidSites.get_urls(i, crawler.link) for i in crawler.pages], []
        )
        if not urls:
            raise commands.BadArgument("No chapters found")
        if len(urls) > 2000:
            raise commands.BadArgument("More than 2000 chapters found")
        text_ = await self.bot.loop.run_in_executor(None, crawler.scraper.get, urls[0])
        text_ = trafilatura.extract(text_.content)
        language = await translator.detect(text_)
        if not await crawler.check_library(inter, language, title):
            return
        text = await self.bot.loop.run_in_executor(
            None, crawler.bucket_scrape, inter, urls, self.crawler_tasks, inter.user.id
        )
        await inter.edit_original_response(embed=self._build_embed("Crawling complete", *args))
        if translate:
            if language != Languages.from_string(translate_to):
                await inter.edit_original_response(embed=self._build_embed("Translating", *args))
                text = await self.bot.loop.run_in_executor(
                    None,
                    translator.bucket_translate,
                    inter,
                    text,
                    translator_cog.translator_tasks,
                    inter.user.id,
                    translate_to,
                )
                await inter.edit_original_response(embed=self._build_embed("Translation complete", *args))
            await inter.edit_original_response(embed=self._build_embed("No translation required", *args))
        else:
            translate_to = await translator.detect(text[:10000])
        if term:
            await inter.edit_original_response(embed=self._build_embed("Terming", *args))
            text = self.bot.termer.replace_terms(text, term)
            await inter.edit_original_response(embed=self._build_embed("Terming complete", *args))
        await inter.edit_original_response(embed=self._build_embed("Uploading", *args))
        await crawler.distribute_translations(
            inter=inter,
            text=text,
            title=title,
            language=translate_to,
            original_language=language,
            term=term,
            crawled_site=url,
            translator=translator,
            thumbnail=thumbnail,
            description=description,
        )

    @crawl_.autocomplete("translate_to")
    async def crawl_translate_to_autocomplete(
        self, _inter: disnake.ApplicationCommandInteraction, translate_to: str
    ) -> dict[str, str]:
        """Autocomplete for the language parameter."""
        data: list[tuple[str, str]] = [
            (str(lang.name), str(lang.value))
            for lang in Languages
            if lang.name.lower().startswith(translate_to.lower())
        ][0:25]
        return {key: value for key, value in data}

    @crawl_.autocomplete("term")
    async def crawl_term_autocomplete(self, _inter: disnake.ApplicationCommandInteraction, term_: str) -> list[str]:
        """Autocomplete for the term parameter."""
        return [term for term in self.bot.termer.get_categories() if term.lower().startswith(term_.lower())][0:25]

    @crawl.sub_command(name="progress", description="Check the progress of a crawl")
    async def progress(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member | None = None) -> None:
        """Check the progress of a crawl

        Parameters
        ----------
        inter : disnake.ApplicationCommandInteraction
            The interaction
        user : disnake.Member, optional
            The user to check the progress of, by default None
        """
        member = user or inter.user
        if member.id not in self.crawler_tasks:
            raise commands.BadArgument("You have no active crawls")
        prg = AnsiBuilder.to_ansi(self.crawler_tasks.get(member.id, "0%"), Colors.GREEN, Styles.BOLD)
        await inter.edit_original_response(
            embed=disnake.Embed(
                title="Crawl progress",
                description=f"{prg}",
                colour=disnake.Colour.random(),
            )
        )
