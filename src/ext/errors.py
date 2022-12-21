import traceback
import typing as t

import disnake
from disnake.ext import commands

from . import Cog


class ErrorHandler(Cog):
    channel: disnake.TextChannel | None = None

    @staticmethod
    def _build_embeds(error: Exception) -> list[disnake.Embed]:
        exc = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        embeds = []
        for i in range(0, len(exc), 1024):
            embed = disnake.Embed(title="Error", description=f"```py\n{exc[i:i+1024]}```")
            embeds.append(embed)
        return embeds

    @commands.Cog.listener()
    async def on_slash_command_error(
        self, inter: disnake.ApplicationCommandInteraction, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.MissingPermissions):
            return await inter.send(
                "> **You don't have the required permissions to run this command.**", ephemeral=True
            )
        elif isinstance(error, commands.BotMissingPermissions):
            return await inter.send("> **I don't have the required permissions to run this command.**", ephemeral=True)
        elif isinstance(error, commands.CommandOnCooldown):
            return await inter.send(
                f"> **This command is on cooldown. Try again in {error.retry_after:.2f}s.**", ephemeral=True
            )
        elif isinstance(error, commands.MaxConcurrencyReached):
            return await inter.send("> **This command is already running.**", ephemeral=True)
        elif isinstance(error, commands.CheckFailure):
            return await inter.send(f"> **{error}**", ephemeral=True)
        elif isinstance(error, commands.BadArgument):
            return await inter.send(f"> **{error}**", ephemeral=True)
        elif isinstance(error, disnake.NotFound):
            return
        else:
            await inter.send("> **An error occurred while executing this command.**", ephemeral=True)
        whole_error = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        self.bot.logger.error(f"Error in {inter.application_command.name} command: {whole_error}")
        if self.channel is None:
            self.channel = t.cast(
                disnake.TextChannel,
                self.bot.get_channel(self.bot.log_channel) or await self.bot.fetch_channel(self.bot.log_channel),
            )
        await self.channel.send(embeds=self._build_embeds(error))
