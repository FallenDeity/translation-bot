import typing as t

import disnake

from .buttons import Buttons

if t.TYPE_CHECKING:
    from src import TranslationBot

__all__: tuple[str, ...] = ("Paginator",)


class Paginator(disnake.ui.View):
    def __init__(
        self, *, inter: disnake.ApplicationCommandInteraction, pages: list[disnake.Embed], timeout: int = 120
    ) -> None:
        super().__init__(timeout=timeout)
        self.user = inter.user
        self.inter = inter
        self.pages = pages
        self.current_page = 0

    async def interaction_check(self, inter: disnake.MessageInteraction) -> bool:
        result = inter.user == self.user
        if not result:
            await inter.response.send_message("You are not the original user.", ephemeral=True)
        return result

    async def show_embed(self, inter: disnake.MessageInteraction, page: int) -> None:
        self.current_page = page
        await inter.response.edit_message(embed=self.pages[page], view=self)

    async def on_timeout(self) -> None:
        for button in self.children:
            button.disabled = True  # type: ignore
        await self.inter.edit_original_response(view=self)

    @disnake.ui.button(label=Buttons.FIRST.name, style=disnake.ButtonStyle.blurple, emoji=str(Buttons.FIRST.value))
    async def first_page(self, _button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        if self.current_page == 0:
            return await inter.response.send_message("You are already on the first page.", ephemeral=True)
        await self.show_embed(inter, 0)

    @disnake.ui.button(
        label=Buttons.PREVIOUS.name, style=disnake.ButtonStyle.blurple, emoji=str(Buttons.PREVIOUS.value)
    )
    async def previous_page(self, _button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        if self.current_page == 0:
            return await inter.response.send_message("You are already on the first page.", ephemeral=True)
        await self.show_embed(inter, self.current_page - 1)

    @disnake.ui.button(label=Buttons.STOP.name, style=disnake.ButtonStyle.blurple, emoji=str(Buttons.STOP.value))
    async def stop_pages(self, _button: disnake.ui.Button, _inter: disnake.MessageInteraction) -> None:
        await self.inter.delete_original_response()
        self.stop()

    @disnake.ui.button(label=Buttons.NEXT.name, style=disnake.ButtonStyle.blurple, emoji=str(Buttons.NEXT.value))
    async def next_page(self, _button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        if self.current_page == len(self.pages) - 1:
            return await inter.response.send_message("You are already on the last page.", ephemeral=True)
        await self.show_embed(inter, self.current_page + 1)

    @disnake.ui.button(label=Buttons.LAST.name, style=disnake.ButtonStyle.blurple, emoji=str(Buttons.LAST.value))
    async def last_page(self, _button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        if self.current_page == len(self.pages) - 1:
            return await inter.response.send_message("You are already on the last page.", ephemeral=True)
        await self.show_embed(inter, len(self.pages) - 1)

    @classmethod
    async def paginate(
        cls,
        inter: disnake.ApplicationCommandInteraction,
        _bot: "TranslationBot",
        pages: list[disnake.Embed],
        timeout: int = 120,
    ) -> None:
        view = cls(inter=inter, pages=pages, timeout=timeout)
        await inter.response.send_message(embed=pages[0], view=view)
