import typing as t

import disnake

if t.TYPE_CHECKING:
    from src import TranslationBot


__all__: tuple[str, ...] = ("InviteView",)


class InviteView(disnake.ui.View):
    def __init__(self, bot: "TranslationBot", *_: t.Any, timeout: float | None = None) -> None:
        super().__init__(timeout=timeout)
        self.bot = bot
        self.add_item(disnake.ui.Button(label="Invite", url=self.bot.invite_url, emoji="💖"))
        self.add_item(disnake.ui.Button(label="Support", url="https://discord.gg/EN3ECMHEZP", emoji="🖖"))
