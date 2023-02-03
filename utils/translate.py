import concurrent.futures
import time
import typing as t

from deep_translator import GoogleTranslator, MyMemoryTranslator

from core.bot import Raizel


class Translator:
    def __init__(self, bot: Raizel, user: int, language: str) -> None:
        self.bot = bot
        self.user = user
        self.language = language
        self.order = {}

    def translate(self, chapter: t.List[str], num: int) -> t.Tuple[int, t.List[str]]:
        translated = []
        try:
            try:
                translated = GoogleTranslator(
                    source="auto", target=self.language
                ).translate_batch(chapter)
            except:
                time.sleep(3)
                translated = GoogleTranslator(
                    source="auto", target=self.language
                ).translate_batch(chapter)
        except Exception as e:
            try:
                if "text must be a valid text" in str(e):
                    for c in chapter:
                        if not isinstance(c, str) or c.isdigit():
                            chapter.remove(c)
                    translated = GoogleTranslator(source="auto", target=self.language).translate_batch(chapter)
                else:
                    time.sleep(5)
                    while True:
                        chp1 = chapter[:len(chapter) // 2]
                        chp2 = chapter[len(chapter) // 2:]
                        try:
                            translated = GoogleTranslator(source="auto", target=self.language).translate_batch(chp1)
                        except:
                            translated = chp1
                            translated.insert(0, "\n\n--->couldn't translate this part")
                            chapter = chp1
                        try:
                            new_tr = GoogleTranslator(source="auto", target=self.language).translate_batch(chp2)
                        except:
                            chp2.insert(0, "\n\n--->couldn't translate this part")
                            chapter = chp2
                        for tr in new_tr:
                            translated.append(tr)
            except:
                for tr in chapter:
                    translated.append("\n\n--->couldn't translate this part")
                    translated.append(tr)

        return num, translated

    def translates(self, chapters: t.List[str]) -> None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(self.translate, [url], num)
                for num, url in enumerate(chapters)
            ]
            for future in concurrent.futures.as_completed(futures):
                self.order[future.result()[0]] = future.result()[1]
                try:
                    if self.bot.translator[self.user] == "break":
                        raise Exception("Translation stopped")
                except:
                    break
                self.bot.translator[self.user] = f"{len(self.order)}/{len(chapters)}"

    async def start(self, chapters: t.List[str]) -> str:
        await self.bot.loop.run_in_executor(None, self.translates, chapters)
        ordered_story = {
            k: v for k, v in sorted(self.order.items(), key=lambda item: item[0])
        }
        full_story = [i[0] for i in list(ordered_story.values()) if i[0] is not None]
        return "".join(full_story)
