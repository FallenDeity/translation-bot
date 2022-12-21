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

    async def distribute_translations(
        self,
        inter: disnake.ApplicationCommandInteraction,
        translator: "Translator",
        text: str,
        language: str,
        original_language: str,
        name: str,
        termed: bool = False,
        crawled: bool = False,
    ) -> None:
        buffer = BytesIO()
        buffer.write(text.encode("utf-8"))
        buffer.seek(0)
        file = disnake.File(buffer, filename=f"{name}.txt")
        message = f"translated from {original_language} to {language}" if not termed else f"termed {name}"
        message += " and crawled" if crawled else ""
        try:
            msg = await inter.followup.send(
                content=f"> **{inter.user.mention} {message}**",
                file=file,
            )
            url = msg.attachments[0].url if msg else ""
        except disnake.HTTPException:
            if not self.DOWNLOAD_DIRECTORY.exists():
                self.DOWNLOAD_DIRECTORY.mkdir()
            path = self.DOWNLOAD_DIRECTORY / f"{name}.txt"
            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                await f.write(text)
            file = await self.bot.loop.run_in_executor(None, partial(self.bot.mega.upload, path.as_posix()))
            url = await self.bot.loop.run_in_executor(None, self.bot.mega.get_upload_link, file)
            view = disnake.ui.View(timeout=None)
            view.add_item(disnake.ui.Button(label="Novel", url=url, emoji="📖"))
            await inter.send(
                content=f"> **{inter.user.mention} {message}**"
                f"\nYour translation is too uploaded to mega.nz and can be downloaded from [here]({url})",
                view=view,
            )
            path.unlink()
        category = Categories.from_string(name)
        tags = translator.get_tags(name) + Categories.get_tags_from_string(name)
        novel = Novel(
            id=await self.bot.mongo.library.get_novel_id(),
            description="",
            download=url,
            title=name,
            language=Languages.from_string(language),
            original_language=original_language,
            tags=tags,
            category=category,
            rating=0,
            size=round(sys.getsizeof(buffer) / 1024 / 1024, 2),
            uploader=inter.user.id,
        )
        await self.bot.mongo.library.add_novel(novel)
        self.bot.dispatch("novel_add", novel)

    async def check_library(self, inter: disnake.ApplicationCommandInteraction, language: str, name: str) -> bool:
        if id_ := await self.bot.mongo.library.find_common(language=Languages.from_string(language), title=name):
            result = await CheckView.prompt(
                inter,
                message=f"This novel [`{', '.join(map(str, id_))}`]"
                f" is present in the library, would you like to continue?",
            )
            if not result:
                await inter.edit_original_response(content="> **Cancelled**", view=None)
                return False
            else:
                await inter.edit_original_response(content="> **Continuing...**", view=None)
        await inter.edit_original_response(content="> **Translating...**", view=None)
        return True
