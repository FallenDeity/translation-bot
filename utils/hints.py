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
        "use leaderboard to check your and friend's rank",
        "check library to find novels you need",
        "ping admins in support server to manually restart bot server https://discord.gg/SZxTKASsHq",
        "you can provide us terms in our server we can add it to bot for better translation",
        "join our support server https://discord.gg/SZxTKASsHq",
        "you can translate novel with .tt #library_id (eg .tt #32101)",
        "translate automatically after crawling with adding en(or other lang code)after url in crawl, (eg. .tcrawl "
        "<link> en where en is eng)",
        "novel less than 300kb won't be added in library",
        "you can use .thelp <command> to  get help for the given command. (eg. .thelp translate)",
        "our categorizer depends on keywords shared by volunteers. sometimes it maybe wrong. you can help us by "
        "providing keywords.",
        "you can share images for different categories with us to add in bot",
        "you can translate multiple novels using .tmulti  and attach all text files ",
        "bot can access all discord attachment links but can't access messages from different servers if bot is not "
        "there",
        "you can invite the bot to your server using .tinvite",
        "due to limited resources bot can only do 2-3 tasks at same time.. wait some time if you got bot is "
        "busy message",
        "if you have any suggestion use suggestion command to send your suggestion",
        "if you found any bugs you can report to us using suggestion command",
    ]

    @classmethod
    async def get_single_hint(cls):
        return random.choice(cls.hints)

