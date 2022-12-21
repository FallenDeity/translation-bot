import typing as t

from disnake.ext import commands

if t.TYPE_CHECKING:
    from src import TranslationBot


__all__: tuple[str, ...] = ("Cog",)


class Cog(commands.Cog):
    def __init__(self, bot: "TranslationBot") -> None:
        self.bot = bot
