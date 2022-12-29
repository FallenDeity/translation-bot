import os
import re
import typing as t
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

import deep_translator.exceptions
import textblob
import translators.server as server
from charset_normalizer import detect
from deep_translator import GoogleTranslator, single_detection
from PyDictionary import PyDictionary

from src.assets import Languages, Termer

from .base_session import BaseSession

if t.TYPE_CHECKING:
    import pathlib

    from src import TranslationBot


__all__: tuple[str, ...] = ("Translator",)


class Translator(BaseSession):
    def __init__(self, *, bot: "TranslationBot", source: str = "auto", target: str = "en") -> None:
        self.bot = bot
        self._translator = GoogleTranslator(source=source, target=target)
        self.dictionary = PyDictionary()
        super().__init__(bot=bot)

    @staticmethod
    def get_tags(text: str) -> list[str]:
        return [i.lower() for i in textblob.TextBlob(text).noun_phrases]

    @staticmethod
    def get_encoding(data: bytes) -> str:
        encoding = detect(data).get("encoding", "utf-8")
        return str(encoding)

    async def format_name(self, name: str) -> str:
        name = await self.translate(name, target=Languages.English.value)
        name = name.split(".")[0]
        name = re.sub(r"[^a-zA-Z,' ]", " ", name).title().strip().replace("é", "e")
        name = re.sub(r"\s+", " ", name)
        return name

    async def check_name(self, name: str) -> bool:
        name = re.sub(r"[^a-zA-Z,' ]", " ", name).strip()
        segment = 0
        for word in name.split():
            if ((w := self.dictionary.meaning(word, disable_errors=True)) and "Noun" in w and len(
                    word) >= 3) or word.lower() in Termer().get_terms():
                segment += 1
                if segment > 2 or len(word) >= 6:
                    return True
        return False

    def translate_(self, text: str, **kwargs: t.Any) -> str:
        self._translator._target = kwargs.get("target", self._translator.target) if kwargs else self._translator.target
        return self._translator.translate(text, **kwargs)

    async def translate(self, text: str, **kwargs: t.Any) -> str:
        self._translator._target = kwargs.get("target", self._translator.target) if kwargs else self._translator.target
        return await self.bot.loop.run_in_executor(None, partial(self._translator.translate, text=text, **kwargs))

    async def translate_file(self, file: t.Union[str, "pathlib.Path"], **kwargs: t.Any) -> str:
        self._translator._target = kwargs.get("target", self._translator.target) if kwargs else self._translator.target
        return await self.bot.loop.run_in_executor(None, partial(self._translator.translate_file, file, **kwargs))

    async def translate_batch(self, batch: list[str], **kwargs: t.Any) -> list[str]:
        self._translator._target = kwargs.get("target", self._translator.target) if kwargs else self._translator.target
        return await self.bot.loop.run_in_executor(None, partial(self._translator.translate_batch, batch, **kwargs))

    async def detect(self, text: str) -> str:
        lang = await self.bot.loop.run_in_executor(None, partial(single_detection, text, os.getenv("DETECT")))
        return Languages.from_string(lang)

    def _task(self, text: str, i: int, data: dict[int, str], target: str) -> None:
        try:
            data[i] = self.translate_(text, target=target)
        except deep_translator.exceptions.RequestError:
            data[i] = server.google(text, to_language=target)

    def bucket_translate(self, text: str, progress: dict[int, str], user_id: int, target: str) -> str:
        chunks = [text[i : i + 2000] for i in range(0, len(text), 2000)]
        data: dict[int, str] = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            tasks = [executor.submit(self._task, chunk, i, data, target) for i, chunk in enumerate(chunks)]
            for _ in as_completed(tasks):
                progress[user_id] = f"Translating {round((len(data) / len(chunks)) * 100)}%"
                self.bot.logger.info(f"Translating {round((len(data) / len(chunks)) * 100)}% for {user_id}")
        ordered = [text for _, text in sorted(data.items(), key=lambda item: item[0])]
        return "".join(ordered)
