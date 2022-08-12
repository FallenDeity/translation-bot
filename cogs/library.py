import discord
import datetime
from discord.ext import commands
from discord import app_commands
from reactionmenu import ViewButton, ViewMenu

from core.bot import Raizel
from databases.data import Novel


class Library(commands.Cog):
    def __init__(self, bot: Raizel) -> None:
        self.bot = bot

    @staticmethod
    def common_elements_finder(*args):
        initial = set(args[0])
        for arg in args[1:]:
            initial = initial.intersection(set(arg))
        return list(initial)

    @staticmethod
    async def buttons(lst: list[discord.Embed], ctx: commands.Context) -> None:
        menu = ViewMenu(ctx, menu_type=ViewMenu.TypeEmbed)
        for i in lst:
            menu.add_page(i)
        back = ViewButton(
            style=discord.ButtonStyle.blurple,
            emoji="<:ArrowLeft:989134685068202024>",
            custom_id=ViewButton.ID_PREVIOUS_PAGE,
        )
        after = ViewButton(
            style=discord.ButtonStyle.blurple,
            emoji="<:rightArrow:989136803284004874>",
            custom_id=ViewButton.ID_NEXT_PAGE,
        )
        stop = ViewButton(
            style=discord.ButtonStyle.blurple,
            emoji="<:dustbin:989150297333043220>",
            custom_id=ViewButton.ID_END_SESSION,
        )
        ff = ViewButton(
            style=discord.ButtonStyle.blurple,
            emoji="<:DoubleArrowRight:989134892384256011>",
            custom_id=ViewButton.ID_GO_TO_LAST_PAGE,
        )
        fb = ViewButton(
            style=discord.ButtonStyle.blurple,
            emoji="<:DoubleArrowLeft:989134953142956152>",
            custom_id=ViewButton.ID_GO_TO_FIRST_PAGE,
        )
        menu.add_button(fb)
        menu.add_button(back)
        menu.add_button(stop)
        menu.add_button(after)
        menu.add_button(ff)
        return await menu.start()

    async def make_base_embed(self, data: Novel) -> discord.Embed:
        embed = discord.Embed(
            title=f"**#{data._id} \t•\t {data.title}**",
            url=data.download,
            description=f"*{data.description}*"
            if data.description
            else "No description.",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Tags", value=f'```yaml\n{", ".join(data.tags)}```')
        embed.add_field(name="Language", value=data.language)
        embed.add_field(name="Size", value=f"{round(data.size/(1024**2), 2)} MB")
        uploader = self.bot.get_user(data.uploader) or await self.bot.fetch_user(
            data.uploader
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.set_footer(
            text=f"ON {datetime.datetime.fromtimestamp(data.date).strftime('%m/%d/%Y, %H:%M:%S')} • {uploader} • {'⭐'*int(data.rating)}",
            icon_url=uploader.display_avatar,
        )
        return embed

    async def make_list_embed(self, data: list[Novel]) -> list[discord.Embed]:
        embeds = []
        for novel in data:
            embeds.append(await self.make_base_embed(novel))
        return embeds

    @commands.hybrid_group()
    async def library(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @library.command(name="search", help="searches a novel in library.")
    async def search(
        self,
        ctx: commands.Context,
        _id: int = None,
        title: str = None,
        language: str = None,
        rating: int = None,
        *,
        tags: str = None,
    ) -> None:
        await ctx.send("Searching...", delete_after=5)
        tags = [i.strip() for i in tags.split() if i] if tags else None
        if (
            _id is None
            and title is None
            and language is None
            and rating is None
            and tags is None
        ):
            novels = await self.bot.mongo.library.get_all_novels
            await self.buttons(await self.make_list_embed(novels), ctx)
            return
        if _id:
            _id = [await self.bot.mongo.library.get_novel_by_id(_id)]
        elif title:
            title = await self.bot.mongo.library.get_novel_by_name(title)
        elif tags:
            tags = await self.bot.mongo.library.get_novel_by_tags(tags)
        elif language:
            language = await self.bot.mongo.library.get_novel_by_language(language)
        elif rating:
            rating = await self.bot.mongo.library.get_novel_by_rating(rating)
        allnovels = self.common_elements_finder(_id, title, tags, language, rating)
        if not allnovels:
            await ctx.send("No novels found.")
            return
        await self.buttons(await self.make_list_embed(allnovels), ctx)

    @search.autocomplete("language")
    async def translate_complete(
            self, inter: discord.Interaction, language: str
    ) -> list[app_commands.Choice]:
        lst = [i for i in self.bot.all_langs if language.lower() in i.lower()][:25]
        return [app_commands.Choice(name=i, value=i) for i in lst]

    @search.autocomplete("tags")
    async def translate_complete(
            self, inter: discord.Interaction, tag: str
    ) -> list[app_commands.Choice]:
        lst = [i for i in await self.bot.mongo.library.get_all_tags if tag.lower() in i.lower()][:25]
        return [app_commands.Choice(name=i, value=i) for i in lst]

    @search.autocomplete("title")
    async def translate_complete(
            self, inter: discord.Interaction, title: str
    ) -> list[app_commands.Choice]:
        lst = [i for i in await self.bot.mongo.library.get_all_titles if title.lower() in i.lower()][:25]
        return [app_commands.Choice(name=i, value=i) for i in lst]

    @library.command(name="info", help="shows info about a novel.")
    async def info(self, ctx: commands.Context, _id: int) -> None:
        novel = await self.bot.mongo.library.get_novel_by_id(_id)
        if not novel:
            await ctx.send("No novel found.")
            return
        embed = await self.make_base_embed(novel)
        await ctx.send(embed=embed)


async def setup(bot: Raizel) -> None:
    await bot.add_cog(Library(bot))
