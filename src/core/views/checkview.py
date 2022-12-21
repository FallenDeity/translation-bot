import disnake

__all__: tuple[str, ...] = ("CheckView",)


class CheckView(disnake.ui.View):
    def __init__(self, *, inter: disnake.ApplicationCommandInteraction, timeout: int = 120):
        super().__init__(timeout=timeout)
        self.user = inter.user
        self.inter = inter
        self.result: bool = False

    async def interaction_check(self, inter: disnake.MessageInteraction) -> bool:
        result = inter.user == self.user
        if not result:
            await inter.response.send_message("You are not the original user.", ephemeral=True)
        return result

    async def on_timeout(self) -> None:
        for button in self.children:
            button.disabled = True  # type: ignore
        await self.inter.edit_original_response(view=self)

    @disnake.ui.button(label="Yes", style=disnake.ButtonStyle.green, emoji="✅")
    async def yes(self, _button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        await inter.response.defer()
        self.result = True
        self.stop()

    @disnake.ui.button(label="No", style=disnake.ButtonStyle.red, emoji="❌")
    async def no(self, _button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        await inter.response.defer()
        self.result = False
        self.stop()

    @classmethod
    async def prompt(
        cls, inter: disnake.ApplicationCommandInteraction, *, timeout: int = 120, message: str | None = None
    ) -> bool:
        view = cls(inter=inter, timeout=timeout)
        await inter.edit_original_response(message, view=view)
        await view.wait()
        for button in view.children:
            button.disabled = True  # type: ignore
        await inter.edit_original_response(view=view)
        return view.result
