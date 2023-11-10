import discord
from discord.ext import commands

from core import Raizel


class ButtonsV(discord.ui.View):
    def __init__(self, bot: Raizel, ctx: commands.Context, task: str, *, timeout=150):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
        self.task = task

    async def check_user_task(self, interaction):
        # Check if the user is the one who initiated the task
        if self.ctx.author.id != interaction.user.id:
            await interaction.response.send_message("Different user.")
            return False
        return True

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.success, emoji='❌')
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_user_task(interaction):
            return
        if self.task == "crawlnext" and self.ctx.author.id in self.bot.crawler_next:
            self.bot.crawler_next[self.ctx.author.id] = "break"
            await interaction.response.send_message("Stopping the crawl next task.")
        elif self.task == "crawl" and self.ctx.author.id in self.bot.crawler:
            self.bot.crawler[self.ctx.author.id] = "break"
            await interaction.response.send_message("Stopping the crawl task.")
        elif self.task == "translate" and self.ctx.author.id in self.bot.translator:
            self.bot.translator[self.ctx.author.id] = "break"
            await interaction.response.send_message("Stopping the translation task.")
        else:
            await interaction.response.send_message("No active task to cancel.")
