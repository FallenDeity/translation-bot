from itertools import chain, starmap
import discord
from discord import ui
from core.bot import Raizel
from discord.ext import commands, menus


class MyMenuPages(ui.View, menus.MenuPages):
    def __init__(self, source, *, delete_message_after=False):
        super().__init__(timeout=60)
        self._source = source
        self.current_page = 0
        self.ctx = None
        self.message = None
        self.delete_message_after = delete_message_after

    async def start(self, ctx, *, channel=None, wait=False):
        await self._source._prepare_once()
        self.ctx = ctx
        self.message = await self.send_initial_message(ctx, ctx.channel)

    async def _get_kwargs_from_page(self, page):
        value = await super()._get_kwargs_from_page(page)
        if "view" not in value:
            value.update({"view": self})
        return value

    async def interaction_check(self, interaction):
        return interaction.user == self.ctx.author

    @ui.button(
        emoji="<:DoubleArrowLeft:989134953142956152>",
        style=discord.ButtonStyle.blurple,
    )
    async def first_page(self, button, interaction):
        await button.response.defer()
        return await self.show_page(0)

    @ui.button(
        emoji="<:ArrowLeft:989134685068202024>", style=discord.ButtonStyle.blurple
    )
    async def before_page(self, button, interaction):
        await button.response.defer()
        return await self.show_checked_page(self.current_page - 1)

    @ui.button(emoji="<:dustbin:989150297333043220>", style=discord.ButtonStyle.blurple)
    async def stop_page(self, button, interaction):
        self.stop()
        if self.delete_message_after:
            return await self.message.delete(delay=0)

    @ui.button(
        emoji="<:rightArrow:989136803284004874>", style=discord.ButtonStyle.blurple
    )
    async def next_page(self, button, interaction):
        await button.response.defer()
        return await self.show_checked_page(self.current_page + 1)

    @ui.button(
        emoji="<:DoubleArrowRight:989134892384256011>",
        style=discord.ButtonStyle.blurple,
    )
    async def last_page(self, button, interaction):
        await button.response.defer()
        return await self.show_page(self._source.get_max_pages() - 1)


class HelpPageSource(menus.ListPageSource):
    def __init__(self, data, helpcommand, mode):
        super().__init__(data, per_page=3)
        self.helpcommand = helpcommand
        self.mode = mode

    def format_command_help(self, no, command):
        signature = (
            str(self.helpcommand.get_command_signature(command))
            .lower()
            .replace("=none", "")
        )
        signature += (30 - len(signature)) * " "
        docs = command.short_doc or "Command is not documented."
        return f"**`{no})`  {command.qualified_name.title()}**```\n{signature}             ```*{docs}*".replace(
            "[", "<"
        ).replace(
            "]", ">"
        )

    async def format_page(self, menu, entries):
        page = menu.current_page
        max_page = self.get_max_pages()
        starting_number = page * self.per_page + 1
        iterator = starmap(
            self.format_command_help, enumerate(entries, start=starting_number)
        )
        page_content = "\n\n".join(iterator)
        embed = discord.Embed(
            title=f"{self.mode} Command",
            description=page_content,
            color=discord.Color.random(),
        )
        author = menu.ctx.author
        embed.set_thumbnail(url=menu.ctx.bot.user.display_avatar)
        embed.set_footer(
            text=f"{page + 1}/{max_page} | Requested by {author.name}",
            icon_url=author.display_avatar,
        )  # author.avatar in 2.0
        return embed


class MyHelp(commands.MinimalHelpCommand):
    async def send_bot_help(self, mapping):
        all_commands = list(chain.from_iterable(mapping.values()))
        formatter = HelpPageSource(all_commands, self, "Help")
        menu = MyMenuPages(formatter, delete_message_after=True)
        await menu.start(self.context)

    async def send_group_help(self, group):
        subcommands = group.commands
        if len(subcommands) == 0:
            return await self.send_command_help(group)
        filtered = await self.filter_commands(subcommands, sort=True)
        filtered.insert(0, group)
        formatter = HelpPageSource(filtered, self, f"{group.qualified_name}")
        menu = MyMenuPages(formatter, delete_message_after=True)
        await menu.start(self.context)

    async def send_command_help(self, command):
        embed = discord.Embed(
            color=discord.Color.random(),
            title=f"{command.qualified_name.title()} Command",
        )
        if command.description:
            embed.description = f"{command.description}\n\n{command.help}"
        else:
            embed.description = command.help or "No help found..."
        embed.add_field(
            name="Usage",
            value=f"```{self.get_command_signature(command).lower().replace('=none', '')}```",
        )
        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(command.aliases))
        embed.set_thumbnail(url=self.context.bot.user.display_avatar)
        embed.set_footer(text=f"Requested by {self.context.author.name}")
        await self.context.send(embed=embed)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.help_command = MyHelp()
        bot.help_command.cog = self


async def setup(bot: Raizel) -> None:
    await bot.add_cog(Help(bot))