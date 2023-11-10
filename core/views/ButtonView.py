import discord
from discord.ext import commands

from core import Raizel


class ButtonsV(discord.ui.View):
    def __init__(self, bot: Raizel, ctx: commands.Context, task: str, *, timeout=150):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.ctx = ctx
        self.task = task

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.success, emoji='❌')
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("here")
        print(interaction)
        if self.task == "crawlnext" and self.ctx.author.id in self.bot.crawler_next:
            self.bot.crawler_next[self.ctx.author.id] = "break"
        if self.task == "crawl" and self.ctx.author.id in self.bot.crawler:
            self.bot.crawler[self.ctx.author.id] = "break"
        if self.task == "translate" and self.ctx.author.id in self.bot.translator:
            self.bot.translator[self.ctx.author.id] = "break"
        await interaction.response.send_message("Stopping the task")



    # @discord.ui.button(label="No", style=discord.ButtonStyle.danger, emoji='👎')
    # async def downvote_button(self, button : discord.ui.Button, interaction : discord.Interaction):
    #     pass