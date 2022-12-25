import pathlib
import sys
import typing as t
from functools import partial
from io import BytesIO

import aiofiles
import disnake

from src.assets import Categories, Languages
from src.core.views import CheckView
from src.database.models import Novel

if t.TYPE_CHECKING:
    from src import TranslationBot
    from src.utils import Translator


class BaseSession:
    DOWNLOAD_DIRECTORY: pathlib.Path = pathlib.Path("bin")

    def __init__(self, *, bot: "TranslationBot") -> None:
        self.bot = bot

    @staticmethod
    def _build_embed(
        inter: disnake.ApplicationCommandInteraction,
        translated: bool,
        title: str,
        description: str,
        thumbnail: str,
        term: str,
        language: str,
        url: str,
        mega: bool,
    ) -> disnake.Embed:
        embed = disnake.Embed(
            title=f"</{inter.application_command.qualified_name}> Command Report",
            color=disnake.Colour.random(),
            description=f"```md\n# {title}\n{description}```",
        )
        if translated:
            embed.add_field(name="Translated to", value=f"```css\n[{language}]```", inline=True)
        if term:
            embed.add_field(name="Termed", value=f"```css\n[{term}]```", inline=True)
        if url:
            embed.add_field(name="Crawled from", value=f"[This link]({url})", inline=True)
        embed.set_footer(text=f"Requested by {inter.user}", icon_url=inter.user.display_avatar.url)
        if mega:
            embed.add_field(
                name="Mega.nz",
                value=f"*The file is too large to be sent as a message, so it was"
                f" uploaded to mega.nz and can be downloaded from [here]({url})*",
                inline=False,
            )
        embed.set_thumbnail(url=thumbnail)
        return embed

    async def distribute_translations(
        self,
        *,
        inter: disnake.ApplicationCommandInteraction,
        translator: "Translator",
        text: str,
        language: str,
        original_language: str,
        title: str,
        term: str = "",
        crawled_site: str = "",
        thumbnail: str = "",
        description: str = "",
    ) -> Novel:
        description = text[:300] + "..." if not description else description
        buffer = BytesIO()
        buffer.write(text.encode("utf-8"))
        buffer.seek(0)
        file = disnake.File(buffer, filename=f"{title}.txt")
        view = None
        try:
            url = ""
        except disnake.HTTPException:
            if not self.DOWNLOAD_DIRECTORY.exists():
                self.DOWNLOAD_DIRECTORY.mkdir()
            path = self.DOWNLOAD_DIRECTORY / f"{title}.txt"
            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                await f.write(text)
            file = await self.bot.loop.run_in_executor(None, partial(self.bot.mega.upload, path.as_posix()))
            url = await self.bot.loop.run_in_executor(None, self.bot.mega.get_upload_link, file)
            view = disnake.ui.View(timeout=None)
            view.add_item(disnake.ui.Button(label="Novel", url=url, emoji="📖"))
            path.unlink()
            view = disnake.ui.View(timeout=None)
            view.add_item(disnake.ui.Button(label="Novel", url=url, emoji="📖"))
        category = Categories.from_string(title)
        tags = translator.get_tags(title) + Categories.get_tags_from_string(title)
        thumbnail = Categories.thumbnail_from_category(category) if not thumbnail else thumbnail
        args = (
            inter,
            language == original_language,
            title,
            description,
            thumbnail,
            term,
            language,
            url,
            bool(view),
        )
        size = round(sys.getsizeof(buffer) / 1024 / 1024, 2)
        msg = await inter.edit_original_response(embed=self._build_embed(*args), view=view)
        novel = Novel(
            id=await self.bot.mongo.library.validate_position(title, language, size),
            description=description,
            download=msg.attachments[0].url if msg.attachments else url,
            title=title,
            language=Languages.from_string(language),
            original_language=original_language,
            tags=tags,
            category=category,
            rating=0,
            size=size,
            uploader=inter.user.id,
            thumbnail=Categories.thumbnail_from_category(category),
            crawled_source=crawled_site,
        )
        await self.bot.mongo.library.add_novel(novel)
        self.bot.dispatch("novel_add", novel, url, file if isinstance(file, disnake.File) else None)
        return novel

    async def check_library(self, inter: disnake.ApplicationCommandInteraction, language: str, name: str) -> bool:
        if id_ := await self.bot.mongo.library.find_common(language=Languages.from_string(language), title=name):
            result = await CheckView.prompt(
                inter,
                message=f"This novel [`{', '.join(map(str, id_))}`]"
                f" is present in the library, would you like to continue?",
            )
            if not result:
                await inter.edit_original_response(
                    embed=disnake.Embed(title="Process cancelled", color=disnake.Colour.red())
                )
                return False
            else:
                await inter.edit_original_response(
                    embed=disnake.Embed(title="Process resumed...", color=disnake.Colour.green())
                )
        return True
