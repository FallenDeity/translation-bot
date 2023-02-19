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
        "add ongoing or complete at end of filename if u got invalid novelname error.."
        "remember filename should be correct unless u wanna get banned from bot",
        "remember always use correct novelname, otherwise u will be banned from bot after 1 warning",
        "feel free to drop your suggestion to us using suggestions command",
        "we can't crawl sites which have high level cloudflare protection",
        "we(bot-admins) can ban you from using bot, if you don't use proper novelname when translating"
    ]

    urls: list[str] = [
        "https://cdn.discordapp.com/attachments/1055445441958916167/1066410851340398774/anime-power-up.gif",
        "https://cdn.discordapp.com/attachments/1055445441958916167/1066410872886530158/animesher.com_asuna--cute-1406639.gif",
        "https://cdn.discordapp.com/attachments/1055445441958916167/1066410928096149604/84f116649b7edefeb6e32754cc8e4ef5.gif",
        "https://cdn.discordapp.com/attachments/1055445441958916167/1066411009625030707/aniyuki-anime-girl-in-fight-28.gif",
        "https://cdn.discordapp.com/attachments/1055445441958916167/1066411067741319280/8c4a56e630fb17708bb6a692f3934671.gif",
        "https://cdn.discordapp.com/attachments/1055445441958916167/1066411146564874250/72d4e0e2700ca1538354fd95bbb5efd1.gif",
        "https://cdn.discordapp.com/attachments/1055445441958916167/1066411595636424784/image0.gif",
        "https://cdn.discordapp.com/attachments/1055445441958916167/1076828894147117177/de67224d07c99e9357d6bc4f17465761.gif",
        "https://cdn.discordapp.com/attachments/1055445441958916167/1076828894507831356/anime-anime-girl.gif",
        "https://cdn.discordapp.com/attachments/1055445441958916167/1076828895296360499/1484029932-f54f0d70e20e33b06f56e35f3aa3926a.gif",
        "https://cdn.discordapp.com/attachments/1055445441958916167/1076828895774515261/fad167493fc0cb0169c3b4c2607fc4cc.gif",
        "https://cdn.discordapp.com/attachments/1055445441958916167/1076828896105857094/78fcdf41fbc27797e92a4429c276e2f6.gif",
        "https://cdn.discordapp.com/attachments/1055445441958916167/1076828896546267146/anime-girl-anime.gif",
        ""
    ]

    @classmethod
    async def get_single_hint(cls):
        return random.choice(cls.hints)

    @classmethod
    async def get_avatar(cls):
        return random.choice(cls.urls)

