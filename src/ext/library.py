import disnake
from disnake.ext import commands

from src.assets import Categories, Languages
from src.core.views.paginators import LazyPaginator
from src.database.models import Novel

from . import Cog


class Library(Cog):
    titles: list[str] | None = None

    async def _build_embed(self, novel: Novel) -> disnake.Embed:
        user = self.bot.get_user(novel.uploader) or await self.bot.fetch_user(novel.uploader)
        embed = disnake.Embed(
            title=f"#{novel.id} {novel.title}",
            description=novel.description,
            color=disnake.Color.random(),
            url=novel.download,
        )
        embed.add_field(name="Rating", value=f"{novel.rating}/5", inline=True)
        embed.add_field(name="Language", value=novel.language, inline=True)
        embed.add_field(name="Original Language", value=novel.original_language, inline=True)
        embed.add_field(name="Category", value=novel.category, inline=True)
        embed.add_field(name="Tags", value=f"```fix\n{', '.join(novel.tags)}```", inline=True)
        embed.add_field(name="Size", value=f"{novel.size} MB", inline=True)
        embed.add_field(
            name="Uploader",
            value=f"Uploaded by `{user}` {disnake.utils.format_dt(novel.date, style='R')} ago",
            inline=True,
        )
        embed.add_field(name="Download", value=f"[Click Here]({novel.download})", inline=True)
        if novel.crawled_source:
            embed.add_field(name="Crawled Source", value=f"[Click Here]({novel.crawled_source})", inline=True)
        embed.set_thumbnail(url=novel.thumbnail)
        return embed

    @commands.slash_command(name="library", description="Get the bot's library.")
    async def library(self, inter: disnake.ApplicationCommandInteraction) -> None:
        """Get the bot's library."""
        await inter.response.defer()

    @library.sub_command(name="search", description="Search the bot's library.")
    async def library_search(
        self,
        inter: disnake.ApplicationCommandInteraction,
        title: str = "",
        rating: commands.Range[0, 5.0] = 0,
        language: str = "",
        original_language: str = "",
        tag: str = "",
        category: str = "",
        uploader: disnake.Member | None = None,
        size: commands.Range[0, 100.0] = 0,
    ) -> None:
        """Search the bot's library.

        Parameters
        ----------
        inter : disnake.ApplicationCommandInteraction
            The interaction
        title: str
            The title of the novel.
        rating: float
            The rating of the novel.
        language: str
            The language of the novel.
        original_language: str
            The original language of the novel.
        tag: str
            The tags of the novel.
        category: str
            The category of the novel.
        uploader: disnake.Member
            The uploader of the novel.
        size: float
            The size of the novel.
        """
        if not any([title, rating, language, original_language, tag, category, uploader, size]):
            total_novels = await self.bot.mongo.library.get_novels_count()
            await LazyPaginator.paginate(inter=inter, bot=self.bot, pages=list(range(1, total_novels + 1)))
            return
        user = uploader.id if uploader else None
        total_novels = await self.bot.mongo.library.find_common(
            title, rating, language, original_language, user, category, tag, size
        )
        await LazyPaginator.paginate(inter=inter, bot=self.bot, pages=total_novels)

    @library_search.autocomplete("title")
    async def library_search_title(self, _inter: disnake.ApplicationCommandInteraction, title: str) -> list[str]:
        """Autocomplete the title of the novel."""
        return [i[:100] for i in await self.bot.mongo.library.get_all_titles() if title.lower() in i.lower()][0:25]

    @library_search.autocomplete("language")
    async def library_search_language(
        self, _inter: disnake.ApplicationCommandInteraction, language: str
    ) -> dict[str, str]:
        """Autocomplete the language parameter."""
        data: list[tuple[str, str]] = [
            (str(lang.name), str(lang.name).replace("_", " "))
            for lang in Languages
            if lang.name.lower().startswith(language.lower())
        ][0:25]
        return {key: value for key, value in data}

    @library_search.autocomplete("original_language")
    async def library_search_original_language(
        self, _inter: disnake.ApplicationCommandInteraction, original_language: str
    ) -> dict[str, str]:
        """Autocomplete the original_language parameter."""
        data: list[tuple[str, str]] = [
            (str(lang.name), str(lang.name.replace("_", " ")))
            for lang in Languages
            if lang.name.lower().startswith(original_language.lower())
        ][0:25]
        return {key: value for key, value in data}

    @library_search.autocomplete("tag")
    async def library_search_tag(self, _inter: disnake.ApplicationCommandInteraction, tag: str) -> list[str]:
        """Autocomplete the tag parameter."""
        return [tag_ for tag_ in await self.bot.mongo.library.get_all_tags() if tag_.lower().startswith(tag.lower())][
            0:25
        ]

    @library_search.autocomplete("category")
    async def library_search_category(self, _inter: disnake.ApplicationCommandInteraction, category: str) -> list[str]:
        """Autocomplete the category parameter."""
        return [str(cat.value.name) for cat in Categories if cat.value.name.lower().startswith(category.lower())][0:25]

    @library.sub_command(name="info", description="Get the info of a novel.")
    async def library_info(self, inter: disnake.ApplicationCommandInteraction, novel_id: int) -> None:
        """Get the info of a novel.

        Parameters
        ----------
        inter : disnake.ApplicationCommandInteraction
            The interaction
        novel_id: int
            The ID of the novel.
        """
        novel_id = await self.bot.mongo.library.get_novels_count() if novel_id == -1 else novel_id
        novel = await self.bot.mongo.library.get_novel(novel_id)
        if novel is None:
            await inter.edit_original_response("Novel not found.")
            return
        await inter.edit_original_response(embed=await self._build_embed(novel))

    @library.sub_command(name="random", description="Get a random novel.")
    async def library_random(self, inter: disnake.ApplicationCommandInteraction) -> None:
        """Get a random novel."""
        novel = await self.bot.mongo.library.get_random_novel()
        await inter.edit_original_response(embed=await self._build_embed(novel))

    @commands.slash_command(name="review", description="Review a novel.")
    async def review(
        self, inter: disnake.ApplicationCommandInteraction, novel_id: int, rating: commands.Range[0, 5.0], review: str
    ) -> None:
        """Review a novel.

        Parameters
        ----------
        inter : disnake.ApplicationCommandInteraction
            The interaction
        novel_id: int
            The ID of the novel.
        rating: float
            The rating of the novel.
        review: str
            The review of the novel.
        """
        novel = await self.bot.mongo.library.get_novel(novel_id)
        if novel is None:
            await inter.edit_original_response("Novel not found.")
            return
        await self.bot.mongo.library.update_novel(novel_id, rating=rating, review=review)
        await inter.edit_original_response("Review added.")
