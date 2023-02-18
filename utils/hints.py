import random


class Hints:
    hints: list[str] = [
        "use .tp to check translation progress",
        "use .tcp to check crawler progress",
        "use crawlnext if there are no TOC page",
        "use table of contents(TOC) page url in crawl",
        "crawl command will add all the links and crawl all text from those links, using selector  will improve  result",
        "ping the site url in #bot-add-sites-for-crawling-suggestion channel so we can add",
        "when we add the site to bot, the junk text would be  reduced.",
        "use library random command to get random novels",
        "use .thelp to get help message for bot commands",
        "bot will restart automatically sometimes wait some time before it  start automatically",
        "if you found any bugs report in our server https://discord.gg/SZxTKASsHq",
        "bot uses google translate to translate novels",
        "we can ban you if you use wrong name for the novel",
        "use leaderboard to check your rank"
    ]

    @classmethod
    async def get_single_hint(cls):
        return random.choice(cls.hints)

