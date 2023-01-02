import traceback
import typing as t

import disnake
from disnake.ext import commands

from src.assets import AnsiBuilder, BackgroundColors, Colors, Styles

from . import Cog


class ErrorHandler(Cog):
    channel: disnake.TextChannel | None = None

    @staticmethod
    def _build_embeds(error: Exception | str) -> list[disnake.Embed]:
        exc = (
            "".join(traceback.format_exception(type(error), error, error.__traceback__))
            if isinstance(error, Exception)
            else error
        )
        embeds = []
        data = exc.split("\n")
        exc = "\n".join(data[1:])
        for i in range(0, len(exc), 1024):
            embed = disnake.Embed(
                title="Error",
                description=f"{AnsiBuilder.to_ansi(data[0], Colors.RED, BackgroundColors.WHITE, Styles.BOLD)}\n"
                f"{AnsiBuilder.to_ansi(exc[i:i+1024], Colors.GREEN, Styles.BOLD)}",
            )
            embeds.append(embed)
        return embeds

    @staticmethod
    def _build_embed(error: Exception | str) -> disnake.Embed:
        exc = (
            "".join(traceback.format_exception(type(error), error, error.__traceback__))
            if isinstance(error, Exception)
            else error
        )
        embed = disnake.Embed(title="Error", description=f"```diff\n- {exc}```", color=disnake.Color.red())
        return embed

    @commands.Cog.listener()
    async def on_slash_command_error(
        self, inter: disnake.ApplicationCommandInteraction, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.MissingPermissions):
            return await inter.send(
                embed=self._build_embed(
                    f"You are missing the following permissions: {', '.join(error.missing_permissions)}"
                ),
                ephemeral=True,
            )
        elif isinstance(error, commands.BotMissingPermissions):
            return await inter.send(
                embed=self._build_embed(
                    f"I am missing the following permissions: {', '.join(error.missing_permissions)}"
                ),
                ephemeral=True,
            )
        elif isinstance(error, commands.CommandOnCooldown):
            return await inter.send(
                embed=self._build_embed(f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds."),
                ephemeral=True,
            )
        elif isinstance(error, commands.MaxConcurrencyReached):
            return await inter.send(
                embed=self._build_embed("This command is already running. Try again later."),
                ephemeral=True,
            )
        elif isinstance(error, commands.CheckFailure):
            return await inter.send(
                embed=self._build_embed(
                    f"{error.args[0] if error.args else 'You do not have permission to use this command.'}"
                ),
                ephemeral=True,
            )
        elif isinstance(error, commands.BadArgument):
            return await inter.send(
                embed=self._build_embed(f"Invalid argument: {error}"),
                ephemeral=True,
            )
        elif isinstance(error, disnake.NotFound):
            return
        else:
            await inter.send(
                embed=self._build_embed("An unknown error has occurred. Please try again later."),
                ephemeral=True,
            )
        whole_error = (
            f"{(await inter.original_message()).jump_url} Error in {inter.application_command.name} command:\n"
        )
        whole_error += "".join(traceback.format_exception(type(error), error, error.__traceback__))
        self.bot.logger.error(f"Error in {inter.application_command.name} command: {whole_error}")
        if self.channel is None:
            self.channel = t.cast(
                disnake.TextChannel,
                self.bot.get_channel(self.bot.log_channel) or await self.bot.fetch_channel(self.bot.log_channel),
            )
        await self.channel.send(embeds=self._build_embeds(whole_error))
