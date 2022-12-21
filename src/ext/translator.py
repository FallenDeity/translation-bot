import pathlib
import re
import typing as t

import aiofiles
import disnake
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
    async def on_novel_add(self, novel: "Novel") -> None:
        user = self.bot.get_user(novel.uploader) or await self.bot.fetch_user(novel.uploader)
        self.bot.logger.info(f"{user} uploaded {novel.title} ({novel.id})")

    async def load_novel_from_link(self, link: str) -> str:
        response = await self.bot.http_session.get(link)
        return await response.text(encoding="utf-8")

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
            inter, translator, translated, str(Languages.English.value), original_language, name
        )
        await inter.edit_original_response(content="> **Translation complete**", view=None)

    async def download_from_link(self, link: str) -> tuple[str, str]:
        if match := self.DISCORD.match(link):
            guild_id = int(match.group("guild_id"))
            channel_id = int(match.group("channel_id"))
            message_id = int(match.group("message_id"))
            guild = self.bot.get_guild(guild_id) or await self.bot.fetch_guild(guild_id)
            channel = t.cast(
                disnake.TextChannel, guild.get_channel(channel_id) or await guild.fetch_channel(channel_id)
            )
            message = await channel.fetch_message(message_id)
            link = message.attachments[0].url
            data = await self.load_novel_from_link(link)
            name = message.attachments[0].filename
        elif (match := self.MEGA.match(link)) or (match := self.MEGA_CO_NZ.match(link)):
            file_id = match.group("file_id")
            file_key = match.group("file_key")
            link = f"https://mega.nz/#!{file_id}!{file_key}"
            if not self.DOWNLOAD_DIRECTORY.exists():
                self.DOWNLOAD_DIRECTORY.mkdir()
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
        if await self.bot.mongo.warns.blocked(inter.user.id):
            await inter.response.send_message("You have been blocked from using this bot")
            raise commands.CheckFailure(f"{inter.user} is blocked from using this bot")

    @commands.slash_command(name="translate", description="Translate a novel from one language to another")
    async def translate(self, inter: disnake.ApplicationCommandInteraction) -> None:
        ...

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
        await inter.send("> **Please wait while I translate your novel...**")
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
            text, o_name = await self.download_from_link(link)
        elif file:
            text, o_name = (await file.read()).decode("utf-8"), file.filename
        elif library_id:
            novel = await self.bot.mongo.library.get_novel(library_id)
            text, o_name = await self.download_from_link(novel.download if novel else "")
        else:
            raise commands.BadArgument("Invalid input")
        translator = Translator(bot=self.bot)
        name = await translator.format_name(name=name or o_name)
        await inter.edit_original_response(content=f"> **Translating {name}...**")
        original_language = await translator.detect(text[:10000])
        if term:
            await inter.edit_original_response(content=f"> **Replacing terms {term} ...**")
            text = self.bot.termer.replace_terms(text, term)
            await inter.edit_original_response(content="> **Terming complete**")
        if not await translator.check_name(name):
            raise commands.BadArgument(f"Invalid name {name}")
        if original_language == Languages.from_string(language):
            if term:
                return await translator.distribute_translations(
                    inter, translator, text, language, original_language, name, termed=True
                )
            raise commands.BadArgument("Cannot translate to the same language")
        if not await translator.check_library(inter, language, name):
            return
        translated = await self.bot.loop.run_in_executor(
            None, translator.bucket_translate, text, self.translator_tasks, inter.user.id, language
        )
        language = Languages.from_string(language)
        await translator.distribute_translations(inter, translator, translated, language, original_language, name)
        await inter.edit_original_response(content="> **Translation complete**", view=None)
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
        if not (progress := self.translator_tasks.get(member.id)):
            return await inter.response.send_message("No translation in progress")
        await inter.response.send_message(f"> **{progress}**")

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
        await inter.send("> **Please wait while I translate your novels...**")
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
                await inter.send(f"> **Error: {e}**")
                self.bot.logger.exception(e.with_traceback(e.__traceback__))
                continue
        await inter.edit_original_response("> **Done**")
