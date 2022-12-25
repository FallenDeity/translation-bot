import pathlib
import re
import sys
import typing as t
import zipfile

import aiofiles
import disnake
import psutil
from disnake.ext import commands

from src.assets import Languages
from src.utils import Translator

from . import Cog

if t.TYPE_CHECKING:
    from src.database.models import Novel


class Translate(Cog):
    translator_tasks: dict[int, str] = {}
    DISCORD = re.compile(
        r"https://(canary\.)?discord(app)?\.com/channels/" r"(?P<guild_id>\d+)/(?P<channel_id>\d+)/(?P<message_id>\d+)"
    )
    MEGA = re.compile(r"https://mega\.nz/file/(?P<file_id>[^#]+)(#(?P<file_key>.+))?")
    MEGA_CO_NZ = re.compile(r"https://mega\.co\.nz/#!(?P<file_id>[^!]+)!(?P<file_key>.+)")
    DOWNLOAD_DIRECTORY: pathlib.Path = pathlib.Path("bin")

    @commands.Cog.listener()
    async def on_novel_add(self, novel: "Novel", url: str, file: disnake.File | None) -> None:
        user = self.bot.get_user(novel.uploader) or await self.bot.fetch_user(novel.uploader)
        self.bot.logger.info(f"{user} uploaded {novel.title} ({novel.id})")
        channel = self.bot.get_channel(1005668482475643050) or await self.bot.fetch_channel(1005668482475643050)
        channel = t.cast(disnake.TextChannel, channel)
        embed = disnake.Embed(
            title=novel.title,
            url=url,
            description=novel.description,
            color=disnake.Color.random(),
            timestamp=novel.date,
        )
        embed.set_footer(text=f"Uploaded by {user}", icon_url=user.display_avatar)
        embed.set_thumbnail(url=novel.thumbnail)
        embed.add_field(name="Uploader", value=user.mention, inline=True)
        embed.add_field(name="ID", value=novel.id, inline=True)
        embed.add_field(name="Language", value=novel.language, inline=True)
        embed.add_field(name="Tags", value=", ".join(novel.tags), inline=False)
        embed.add_field(name="Category", value=f"`{novel.category}`", inline=True)
        if novel.crawled_source:
            embed.add_field(name="Crawled Source", value=novel.crawled_source, inline=True)
        view = disnake.ui.View(timeout=None)
        view.add_item(disnake.ui.Button(label="Download", url=url, style=disnake.ButtonStyle.link, emoji="📥"))
        if file:
            await channel.send(embed=embed, file=file, view=view)
            return
        await channel.send(embed=embed, view=view)

    async def load_novel_from_link(self, link: str) -> str:
        head = await self.bot.http_session.head(link)
        if int(head.headers["Content-Length"]) / 1024 / 1024 > 20:
            raise commands.BadArgument("File is too large")
        response = await self.bot.http_session.get(link)
        return await response.text(encoding="utf-8")

    async def load_novel_in_chunks(self, user_id: int, link: str, name: str | None = None) -> list[pathlib.Path]:
        files: list[pathlib.Path] = []
        name = name or link.split("/")[-1].split(".")[0]
        async with self.bot.http_session.get(link) as response:
            data = bytes()
            async for chunk in response.content.iter_chunked(6 * 1024 * 1024):
                file = self.DOWNLOAD_DIRECTORY / f"{name}_{user_id}_{len(files)}.txt"
                data += chunk
                if sys.getsizeof(data) >= 6 * 1024 * 1024:
                    async with aiofiles.open(file, "wb") as f:
                        await f.write(data)
                    self.bot.logger.info(f"Downloaded {file}")
                    files.append(file)
                    data = bytes()
            if data:
                file = self.DOWNLOAD_DIRECTORY / f"{name}_{user_id}_{len(files)}.txt"
                async with aiofiles.open(file, "wb") as f:
                    await f.write(data)
                self.bot.logger.info(f"Downloaded {file}")
                files.append(file)
        return files

    def _zip_files(self, user_id: int, files: list[pathlib.Path]) -> pathlib.Path:
        with zipfile.ZipFile(self.DOWNLOAD_DIRECTORY / f"{user_id}.zip", "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file in files:
                zf.write(file)
            self.bot.logger.info(f"Zipped {len(files)} files")
        return self.DOWNLOAD_DIRECTORY / f"{user_id}.zip"

    async def _minimal_translate(
        self, inter: disnake.ApplicationCommandInteraction, translator: "Translator", name: str, text: str
    ) -> None:
        name = await translator.format_name(name=name)
        await inter.edit_original_response(content=f"> **Translating {name}...**")
        original_language = await translator.detect(text[:10000])
        if not await translator.check_name(name):
            raise commands.BadArgument(f"Invalid name {name}")
        if original_language == Languages.English.name:
            raise commands.BadArgument("Cannot translate to the same language")
        if not await translator.check_library(inter, str(Languages.English.value), name):
            return
        translated = await self.bot.loop.run_in_executor(
            None, translator.bucket_translate, text, self.translator_tasks, inter.user.id, Languages.English.value
        )
        await translator.distribute_translations(
            inter=inter,
            translator=translator,
            text=translated,
            original_language=original_language,
            title=name,
            language=str(Languages.English.value),
        )
        await inter.edit_original_response(content="> **Translation complete**", view=None)

    async def _match_discord_link(self, link: str) -> disnake.Message | None:
        if match := self.DISCORD.match(link):
            guild_id = int(match.group("guild_id"))
            channel_id = int(match.group("channel_id"))
            message_id = int(match.group("message_id"))
            guild = self.bot.get_guild(guild_id) or await self.bot.fetch_guild(guild_id)
            channel = t.cast(
                disnake.TextChannel, guild.get_channel(channel_id) or await guild.fetch_channel(channel_id)
            )
            message = await channel.fetch_message(message_id)
            if message is None or not message.attachments:
                raise commands.BadArgument("Invalid message link")
            return message
        return None

    async def download_from_link(self, link: str) -> tuple[str, str]:
        if self.DISCORD.match(link):
            message = await self._match_discord_link(link)
            assert isinstance(message, disnake.Message)
            link = message.attachments[0].url
            data = await self.load_novel_from_link(link)
            name = message.attachments[0].filename
        elif (match := self.MEGA.match(link)) or (match := self.MEGA_CO_NZ.match(link)):
            file_id = match.group("file_id")
            file_key = match.group("file_key")
            link = f"https://mega.nz/#!{file_id}!{file_key}"
            try:
                path = await self.bot.loop.run_in_executor(
                    None, self.bot.mega.download_url, link, self.DOWNLOAD_DIRECTORY.as_posix()
                )
                name = pathlib.Path(path).name
            except PermissionError:
                path = max(self.DOWNLOAD_DIRECTORY.iterdir(), key=lambda p: p.stat().st_ctime)
                name = path.name
            async with aiofiles.open(path, "r", encoding="utf-8") as f:
                data = await f.read()
            path.unlink()
        else:
            name = link.split("/")[-1]
            data = await self.load_novel_from_link(link)
        return data, name

    async def cog_before_slash_command_invoke(self, inter: disnake.ApplicationCommandInteraction) -> None:
        if not self.DOWNLOAD_DIRECTORY.exists():
            self.DOWNLOAD_DIRECTORY.mkdir()
        if await self.bot.mongo.warns.blocked(inter.user.id):
            raise commands.CheckFailure(f"{inter.user} is blocked from using this bot")

    @commands.slash_command(name="translate", description="Translate a novel from one language to another")
    async def translate(self, _inter: disnake.ApplicationCommandInteraction) -> None:
        if psutil.virtual_memory().percent > 90:
            raise commands.CheckFailure("Bot is under heavy load")
        if _inter.user.id in self.translator_tasks:
            raise commands.CheckFailure("You are already translating a novel")
        await _inter.response.defer()

    @translate.sub_command(name="translate", description="Translate a novel")
    @commands.max_concurrency(1, commands.BucketType.user)
    async def translate_(
        self,
        inter: disnake.ApplicationCommandInteraction,
        link: str | None = None,
        file: disnake.Attachment | None = None,
        library_id: int | None = None,
        language: str = "en",
        name: str | None = None,
        term: str | None = None,
    ) -> None:
        """Translate a novel.

        Parameters
        ----------
        inter : disnake.ApplicationCommandInteraction
            The interaction.
        link: str
            The link to the novel.
        file: disnake.Attachment
            The file to translate.
        library_id: int
            The library id to translate.
        language: str
            The language to translate to.
        name: str
            The name of the novel.
        term: str
            The terms to replace.
        """
        await inter.send(
            embed=disnake.Embed(title="Translating...", description="Please wait...", colour=disnake.Colour.random())
        )
        if not any([link, file, library_id]):
            raise commands.BadArgument("You must provide a link, file, or library id")
        if link and not link.startswith("https://"):
            raise commands.BadArgument("Invalid link")
        if library_id and not (await self.bot.mongo.library.get_novel(library_id)):
            raise commands.BadArgument("Invalid library id")
        if language not in Languages.all_languages():
            raise commands.BadArgument("Invalid language")
        if term and term not in self.bot.termer.get_categories():
            raise commands.BadArgument("Invalid term")
        if link:
            await inter.edit_original_response(
                embed=disnake.Embed(
                    title="Downloading...", description="Please wait...", colour=disnake.Colour.random()
                )
            )
            text, o_name = await self.download_from_link(link)
        elif file:
            text, o_name = (await file.read()).decode("utf-8"), file.filename
        elif library_id:
            await inter.edit_original_response(
                embed=disnake.Embed(
                    title="Downloading...", description="Please wait...", colour=disnake.Colour.random()
                )
            )
            novel = await self.bot.mongo.library.get_novel(library_id)
            text, o_name = await self.download_from_link(novel.download if novel else "")
        else:
            raise commands.BadArgument("Invalid input")
        if not text or not o_name:
            raise commands.BadArgument("Invalid input")
        translator = Translator(bot=self.bot)
        name = await translator.format_name(name=name or o_name)
        await inter.edit_original_response(
            embed=disnake.Embed(
                title="Translating...", description="Translation started...", colour=disnake.Colour.random()
            )
        )
        original_language = await translator.detect(text[:10000])
        if term:
            await inter.edit_original_response(
                embed=disnake.Embed(
                    title="Terming...", description="Replacing terms...", colour=disnake.Colour.random()
                )
            )
            text = self.bot.termer.replace_terms(text, term)
            await inter.edit_original_response(
                embed=disnake.Embed(
                    title="Terming...", description="Terming complete...", colour=disnake.Colour.random()
                )
            )
        if not await translator.check_name(name):
            raise commands.BadArgument(f"Invalid name {name}")
        if original_language == Languages.from_string(language):
            if term:
                await translator.distribute_translations(
                    inter=inter,
                    translator=translator,
                    text=text,
                    title=name,
                    original_language=original_language,
                    language=language,
                    term=term,
                )
                return
            raise commands.BadArgument("Cannot translate to the same language")
        if not await translator.check_library(inter, language, name):
            return
        translated = await self.bot.loop.run_in_executor(
            None, translator.bucket_translate, text, self.translator_tasks, inter.user.id, language
        )
        language = Languages.from_string(language)
        await inter.edit_original_response(
            embed=disnake.Embed(
                title="Translating...", description="Translation complete...", colour=disnake.Colour.random()
            )
        )
        await translator.distribute_translations(
            inter=inter,
            translator=translator,
            text=translated,
            title=name,
            original_language=original_language,
            language=language,
        )
        self.translator_tasks.pop(inter.user.id)

    @translate_.autocomplete("language")
    async def translate_language_autocomplete(
        self, _inter: disnake.ApplicationCommandInteraction, language: str
    ) -> dict[str, str]:
        """Autocomplete for the language parameter."""
        data: list[tuple[str, str]] = [
            (str(lang.name), str(lang.value)) for lang in Languages if lang.name.lower().startswith(language.lower())
        ][0:25]
        return {key: value for key, value in data}

    @translate_.autocomplete("term")
    async def translate_term_autocomplete(self, _inter: disnake.ApplicationCommandInteraction, term_: str) -> list[str]:
        """Autocomplete for the term parameter."""
        return [term for term in self.bot.termer.get_categories() if term.lower().startswith(term_.lower())][0:25]

    @translate.sub_command(name="progress", description="Get the progress of a translation")
    async def progress(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User | None = None) -> None:
        """Get the progress of a translation.

        Parameters
        ----------
        inter : disnake.ApplicationCommandInteraction
            The interaction.
        user: disnake.User
            The user to get the progress of.
        """
        member = user or inter.user
        if member.id not in self.translator_tasks:
            raise commands.BadArgument("You have no active translations")
        await inter.send(
            embed=disnake.Embed(
                title="Crawl progress",
                description=f"```elixir\n{self.translator_tasks[member.id]}%```",
                colour=disnake.Colour.random(),
            )
        )

    @commands.message_command(name="multi-translate", description="Translate multiple novels")
    @commands.max_concurrency(1, commands.BucketType.user)
    async def multi_translate(self, inter: disnake.ApplicationCommandInteraction, message: disnake.Message) -> None:
        """Translate multiple novels.

        Parameters
        ----------
        inter: disnake.ApplicationCommandInteraction
            The interaction.
        message: disnake.Message
            The message to translate.
        """
        if psutil.virtual_memory().percent > 90:
            raise commands.BadArgument("The bot is currently under heavy load, please try again later")
        await inter.send(
            embed=disnake.Embed(
                title="Translating...", description="Translation started...", colour=disnake.Colour.random()
            )
        )
        links = re.findall(r"https?://\S+", message.content)
        if not links and not message.attachments:
            raise commands.BadArgument("No links or attachments")
        translator = Translator(bot=self.bot)
        for link in links:
            try:
                text, o_name = await self.download_from_link(link)
                await self._minimal_translate(inter, translator, o_name, text)
            except Exception as e:
                await inter.send(f"> **Error: {e}**")
                self.bot.logger.exception(e.with_traceback(e.__traceback__))
                continue
        for attachment in message.attachments:
            try:
                text, o_name = (await attachment.read()).decode("utf-8"), attachment.filename
                await self._minimal_translate(inter, translator, o_name, text)
            except Exception as e:
                await inter.send(
                    embed=disnake.Embed(
                        title="Failed",
                        description="Translation failed for current novel...",
                        colour=disnake.Colour.red(),
                    )
                )
                self.bot.logger.exception(e.with_traceback(e.__traceback__))
                continue
        await inter.edit_original_response(
            embed=disnake.Embed(
                title="Translating...", description="Translation complete...", colour=disnake.Colour.random()
            )
        )

    @commands.slash_command(name="split", description="Split a novel into parts")
    @commands.max_concurrency(1, commands.BucketType.user)
    async def split(self, inter: disnake.ApplicationCommandInteraction, link: str) -> None:
        """
        Split a novel into parts.

        Parameters
        ----------
        inter: disnake.ApplicationCommandInteraction
            The interaction.
        link: str
            The link to the novel.
        """
        await inter.send(
            embed=disnake.Embed(
                title="Splitting...", description="Splitting started...", colour=disnake.Colour.random()
            )
        )
        discord_check = await self._match_discord_link(link)
        if discord_check is None:
            novels = await self.load_novel_in_chunks(user_id=inter.user.id, link=link)
        else:
            file = discord_check.attachments[0]
            novels = await self.load_novel_in_chunks(user_id=inter.user.id, link=file.url, name=file.filename)
        if not novels:
            raise commands.BadArgument("No novels found")
        await inter.edit_original_response(
            embed=disnake.Embed(
                title="Splitting...", description="Splitting complete...", colour=disnake.Colour.random()
            )
        )
        zipped = await self.bot.loop.run_in_executor(None, self._zip_files, inter.user.id, novels)
        if sys.getsizeof(zipped) / 1024 / 1024 >= 8:
            file = await self.bot.loop.run_in_executor(None, self.bot.mega.upload, zipped.as_posix())
            url = await self.bot.loop.run_in_executor(None, self.bot.mega.get_upload_link, file)
            view = disnake.ui.View()
            view.add_item(disnake.ui.Button(label="Download", url=url, emoji="📥"))
            await inter.edit_original_response(
                embed=disnake.Embed(
                    title="Novel Split",
                    description=f"Novel split into parts, download [here]({url})",
                    colour=disnake.Colour.random(),
                ),
                view=view,
            )
        else:
            await inter.edit_original_response(
                embed=disnake.Embed(
                    title="Novel Split", description="Novel split into parts", colour=disnake.Colour.random()
                ),
                file=disnake.File(zipped.as_posix(), filename="novel.zip"),
            )
        for novel in novels:
            novel.unlink()
        zipped.unlink()
