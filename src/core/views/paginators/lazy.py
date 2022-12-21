import typing as t

import disnake

from .classic import Paginator

if t.TYPE_CHECKING:
    from src import TranslationBot


__all__: tuple[str, ...] = ("LazyPaginator",)


class LazyPaginator(Paginator):
    def __init__(
        self,
        *,
        inter: disnake.ApplicationCommandInteraction,
        bot: "TranslationBot",
        pages: list[int],
        timeout: int = 120,
    ) -> None:
        super().__init__(inter=inter, pages=[], timeout=timeout)
        self.per_page = 10
        self.bot = bot
        self.pages: dict[int, list[int]] = {
            n: pages[i : i + self.per_page] for n, i in enumerate(range(0, len(pages), self.per_page))
        }
        self._built_pages: dict[int, disnake.Embed] = {}

    async def _build_page(self, page: int) -> disnake.Embed:
        if page in self._built_pages:
            return self._built_pages[page]
        items = self.pages[page]
        novels = await self.bot.mongo.library.get_novels(items)
        description = ""
        for n, novel in enumerate(novels, start=1):
            description += (
                f"{self.per_page * page + n}﹚ [{novel.title.title()}]({novel.download}) \t◈\t"
                f" {novel.rating}/5 \t◈\t {novel.language} \t◈\t **#{novel.id}**\n\n"
            )
        embed = disnake.Embed(title="Library", description=description, color=disnake.Color.random())
        embed.set_footer(text=f"Page {page + 1}/{len(self.pages)}")
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        self._built_pages[page] = embed
        return embed

    async def show_embed(self, inter: disnake.MessageInteraction, page: int) -> None:
        embed = await self._build_page(page)
        self.current_page = page
        await inter.response.edit_message(embed=embed)

    @classmethod
    async def paginate(
        cls,
        *,
        inter: disnake.ApplicationCommandInteraction,
        bot: "TranslationBot",
        pages: list[int],
        timeout: int = 120,
    ) -> None:
        view = cls(inter=inter, bot=bot, pages=pages, timeout=timeout)
        embed = await view._build_page(0)
        await inter.edit_original_response(embed=embed, view=view)
