import datetime
import random

import discord
import joblib
from discord import app_commands
from discord.ext import commands
from reactionmenu import ViewButton, ViewMenu

from core.bot import Raizel
from databases.data import Novel
from utils.category import Categories
from utils.hints import Hints


class Library(commands.Cog):
    def __init__(self, bot: Raizel) -> None:
        self.bot = bot
        self.sorted_data: list = ["_id", "title", "rating", "size", "uploader", "date"]

    @staticmethod
    def common_elements_finder(*args):
        if len(args) == 1:
            return args[0]
        initial = args[0]
        for arg in args[1:]:
            initial = [i for i in initial for j in arg if i._id == j._id]
        return initial

    @staticmethod
    async def buttons(lst: list[discord.Embed], ctx: commands.Context) -> None:
        if len(lst) == 1:
            return await ctx.send(embed=lst[0])
        menu = ViewMenu(ctx, menu_type=ViewMenu.TypeEmbed, remove_buttons_on_timeout=True)
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
            title=f"**#{data['_id']} \t•\t {data['title'][:240].strip()}**",
            url=data['download'],
            description=f"*{data['description'][:2000]}*"
            if data['description']
            else "No description.",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Category", value=data['category'])
        embed.add_field(name="Tags", value=f'```yaml\n{", ".join(data["tags"])}```')
        if not str(data["org_language"]).lower() == 'na':
            embed.add_field(name="Raw Language", value=data["org_language"])
        embed.add_field(name="Language", value=data["language"])
        embed.add_field(name="Size", value=f"{round(data['size'] / (1024 ** 2), 2)} MB")
        uploader = self.bot.get_user(data['uploader']) or await self.bot.fetch_user(
            data['uploader']
        )
        embed.set_thumbnail(url=data['thumbnail'])
        embed.set_footer(
            text=f"ON {datetime.datetime.fromtimestamp(data['date']).strftime('%m/%d/%Y, %H:%M:%S')} • {uploader} • {'⭐' * int(data['rating'])}",
            icon_url=uploader.display_avatar,
        )
        return embed

    async def make_list_embed(self, data: list[Novel]) -> list[discord.Embed]:
        embeds = []
        for novel in data:
            embeds.append(await self.make_base_embed(novel))
        return embeds

    async def make_base_list_embed(self, data: list[Novel], page: int) -> discord.Embed:
        output = [
            f"**#{novel['_id']}\t💠\t[{novel['title'].split('__')[0].strip()[:200]}]({novel['download']})**\n💠\tSize: **{round(novel['size'] / (1024 ** 2), 2)} MB**\t💠\tLanguage:** {novel['language']}** "
            for novel in data]
        out_str = ""
        for out in output:
            out_str += out + "\n\n"
        embed = discord.Embed(title=f"**Page {page}**",
                              description=out_str)
        embed.set_footer(text=f"Hint : {await Hints.get_single_hint()}", icon_url=await Hints.get_avatar())
        return embed

    async def make_list_embed_list(self, data: list[Novel]) -> list[discord.Embed]:
        embeds = []
        n = 6
        final = [data[i * n:(i + 1) * n] for i in range((len(data) + n - 1) // n)]
        page = 1
        for novel in final:
            embeds.append(await self.make_base_list_embed(novel, page))
            page += 1
        return embeds

    @commands.hybrid_group()
    async def library(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @library.command(name="search",
                     help="searches a novel in library. Shuffle is turned on by default. Use sort_by for sorting novels")
    async def search(
            self,
            ctx: commands.Context,
            title: str = None,
            language: str = None,
            rating: int = 0,
            show_list: bool = False,
            category: str = None,
            tags: str = None,
            raw_language: str = None,
            size: float = None,
            uploader: discord.User = None,
            shuffle: bool = True,
            sort_by: str = None,
            no_of_novels: int = 300,
    ) -> None:
        """Searches a novel in library
               Parameters
               ----------
               ctx : commands.Context
                   The interaction
               title : str, optional
                   Title of the novel, bot will auto-suggest novels in library
               language :
                    Language of the novel
               rating :
                    rating of the novel must be between 0 to 5
               show_list :
                    give true if you need it in list view by default it  is false
               category :
                    category of novel
               tags :
                    tags of novel , bot will auto suggest
               raw_language :
                    raw_language of novel
               size :
                    size of novel in mb, bot will give novel with more than this size
               uploader :
                    uploader of novel
               shuffle :
                    will shuffle the novel, by default true, if you don't need to shuffle give false
               sort_by :
                    sort the novels according to the value given
               no_of_novels :
                    number of novels you want to get from library
               """
        try:
            await ctx.defer()
        except:
            pass
        msg = await ctx.send("Searching...")
        tags = [i.strip() for i in tags.split() if i] if tags else None
        if uploader:
            uploader_id = uploader.id
        else:
            uploader_id = None
        allnovels = await self.bot.mongo.library.find_common(title=title, tag=tags, rating=rating, category=category, language=language, size=size, original_language=raw_language, uploader=uploader_id, no=no_of_novels)
        if not allnovels or allnovels == []:
            await ctx.send("> **No results found.**")
            await msg.delete()
            return

        if shuffle and sort_by is None:
            random.shuffle(allnovels)
        if sort_by is not None:
            if sort_by not in self.sorted_data:
                await ctx.send(f"> **Given sort by is not present in bot. available filters \n {self.sorted_data}**")
            else:
                if sort_by == "_id":
                    allnovels.sort(key=lambda x: x["_id"])
                elif sort_by == "title":
                    allnovels.sort(key=lambda x: x["title"])
                elif sort_by == "rating":
                    allnovels.sort(key=lambda x: x["rating"])
                    allnovels.reverse()
                elif sort_by == "size":
                    allnovels.sort(key=lambda x: x["size"])
                    allnovels.reverse()
                elif sort_by == "uploader":
                    allnovels.sort(key=lambda x: x["uploader"])
                elif sort_by == "date":
                    allnovels.sort(key=lambda x: x["date"])
                    allnovels.reverse()
        # print("got all novels")
        full_size = 0
        if not allnovels:
            return await ctx.send("> **No results found.**")
        if show_list is True and no_of_novels == 300:
            no_of_novels = 1000
        if len(allnovels) >= no_of_novels:
            full_size = len(allnovels)
            allnovels = allnovels[:no_of_novels]
        if show_list:
            embeds = await self.make_list_embed_list(allnovels)
            if full_size != 0:
                msg = await msg.edit(content=f"> Showing first **{str(no_of_novels)} **")
            else:
                msg = await msg.edit(content=f"> Found **{len(allnovels)}** novels")
            try:
                del allnovels
            except:
                pass
            return await self.buttons(embeds, ctx)
        else:
            embeds = await self.make_list_embed(allnovels)
            if full_size != 0:
                msg = await msg.edit(content=f"> Showing first **{str(no_of_novels)}**")
            else:
                msg = await msg.edit(content=f"> Found **{len(embeds)}** novels")
            try:
                del allnovels
            except:
                pass
            return await self.buttons(embeds, ctx)

    @library.command(name="random", help="Gives 10 random novel in library.")
    async def random(
            self,
            ctx: commands.Context, no_of_novels: int = 10
    ) -> None:
        """get random novels from library
               Parameters
               ----------
               ctx : commands.Context
                   The interaction
               no_of_novels : int, optional
                   number of novels , by default it is 10
               """
        await ctx.defer()
        novels = await self.bot.mongo.library.get_random_novel(no=no_of_novels)
        embeds = await self.make_list_embed(novels)
        return await self.buttons(embeds, ctx)

    @search.autocomplete("language")
    async def translate_complete(
            self, inter: discord.Interaction, language: str
    ) -> list[app_commands.Choice]:
        lst = [i for i in self.bot.all_langs if language.lower() in i.lower()][:25]
        return [app_commands.Choice(name=i, value=i) for i in lst]

    @search.autocomplete("raw_language")
    async def translate_complete(
            self, inter: discord.Interaction, language: str
    ) -> list[app_commands.Choice]:
        lst = [i for i in self.bot.all_langs if language.lower() in i.lower()][:25]
        return [app_commands.Choice(name=i, value=i) for i in lst]

    @search.autocomplete("category")
    async def translate_complete(
            self, inter: discord.Interaction, category: str
    ) -> list[app_commands.Choice]:
        lst = [str(cat.value.name) for cat in Categories if cat.value.name.lower().startswith(category.lower())][0:25]
        return [app_commands.Choice(name=i, value=i) for i in lst]

    @search.autocomplete("sort_by")
    async def translate_complete(
            self, inter: discord.Interaction, language: str
    ) -> list[app_commands.Choice]:
        lst = self.sorted_data
        return [app_commands.Choice(name=i, value=i) for i in lst]

    @search.autocomplete("tags")
    async def translate_complete(
            self, inter: discord.Interaction, tag: str
    ) -> list[app_commands.Choice]:
        lst = [
                  i
                  for i in await self.bot.mongo.library.get_all_tags
                  if tag.lower() in i.lower()
              ][:25]
        return [app_commands.Choice(name=i, value=i) for i in lst]

    @search.autocomplete("title")
    async def translate_complete(
            self, inter: discord.Interaction, title: str
    ) -> list[app_commands.Choice]:
        titles = joblib.load('titles.sav')
        lst = [
                  str(i[:90]).strip()
                  for i in titles
                  if title.lower() in i.lower()
              ][:25]
        # print(lst)
        return [app_commands.Choice(name=i, value=i) for i in lst]

    @library.command(name="info", help="shows info about a novel.")
    async def info(self, ctx: commands.Context, _id: int) -> None:
        """shows info of the novel.
                       Parameters
                       ----------
                       ctx : commands.Context
                           The interaction
                       _id : int
                           library id which you want to view
                       """
        try:
            await ctx.defer()
        except:
            pass
        novel = await self.bot.mongo.library.get_novel_by_id(_id)
        if not novel:
            return await ctx.send("No novel found.")
        embed = await self.make_base_embed(novel)
        return await ctx.send(embed=embed)

    @library.command(name="review", help="reviews a novel.")
    async def review(
            self, ctx: commands.Context, _id: int, rating: int, summary: str
    ) -> None:
        """Review a novel.
               Parameters
               ----------
               ctx : commands.Context
                   The interaction
               _id : int
                   library id which you want to review
               rating : int
                    give your rating from 0 to 5
               summary : str
                    your review comments.
               """
        await ctx.defer()
        if not 0 <= rating <= 5:
            await ctx.send("Rating must be between 0 and 5.")
            return
        novel = await self.bot.mongo.library.get_novel_by_id(_id)
        if not novel:
            await ctx.send("No novel found.")
            return
        description = novel["description"][:500]
        await self.bot.mongo.library.update_description(
            novel["_id"], f"{description}\n\n**{summary} +  • Reviewed by {ctx.author}**"
        )
        if novel["rating"] != 0:
            rating = int((rating + novel["rating"])/2)
        await self.bot.mongo.library.update_rating(novel["_id"], rating)
        await ctx.send("Novel reviewed.")
        await self.bot.get_command("library info").callback(Library(self.bot), ctx, _id)
        channel = await self.bot.fetch_channel(974673230826721290)
        if channel:
            msg = await channel.send(content=f"> {ctx.author} reviewed novel with id #{_id}")
            context = await self.bot.get_context(msg)
            await self.bot.get_command("library info").callback(Library(self.bot), context, _id)

    @commands.hybrid_command(name="leaderboard", description="Get the bot's leaderboard.")
    async def leaderboard(self, ctx: commands.Context, user: discord.User = None) -> None:
        """Check the leaderboard of a user
        Parameters
        ----------
        ctx : commands.Context
            The interaction
        user : discord.User, optional
            The user to check the leaderboard of, by default None
        """
        await ctx.defer()
        if user is None:
            ld_user_id = ctx.author.id
        else:
            ld_user_id = user.id
        user_rank = await self.bot.mongo.library.get_user_novel_count(user_id=ld_user_id)
        top_200 = await self.bot.mongo.library.get_user_novel_count(_top_200=True)
        embeds = []
        top_200 = [(user_id, count) for user_id, count in top_200.items()]
        chunks = [top_200[i: i + 10] for i in range(0, len(top_200), 10)]
        n = 1
        for chunk in chunks:
            embed = discord.Embed(
                title="Leaderboard",
                description=f"**Leaderboard of the bot!**\
                        \n\n**User Rank: {user_rank[ld_user_id]}**",
                color=discord.Color.random(),
            )
            embed.set_footer(text="Thanks for using TranslationBot!", icon_url=self.bot.user.display_avatar)
            embed.set_thumbnail(url=ctx.author.display_avatar)
            for user_id, count in chunk:
                try:
                    embed.add_field(
                        name=f"{n}. {count} novels",
                        value=f"**{(self.bot.get_user(user_id)).name} **-> <@{user_id}>",
                        inline=False,
                    )
                except:
                    pass
                n += 1
            embeds.append(embed)
        return await self.buttons(embeds, ctx)


async def setup(bot: Raizel) -> None:
    await bot.add_cog(Library(bot))
