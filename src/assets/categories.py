import enum

__all__: tuple[str, ...] = ("Categories",)


class Categories(enum.Enum):
    Naruto = "Naruto"
    OnePiece = "One-Piece"
    Marvel = "Marvel"
    DC = "DC"
    HarryPotter = "Harry-Potter"
    Pokemon = "Pokemon"
    ChatRoom = "Chat-Room"
    Villain = "Villain"
    SpiritRecovery = "Spirit-Recovery"
    Fantasy = "Fantasy"
    FairyTail = "Fairy-Tail"
    GenshinImpact = "Genshin-Impact"
    DoulouDaluo = "Doulou-Daluo"
    PreHistoric = "Pre-Historic"
    OnlineGames = "Online-Games"
    Conan = "Conan"
    HighSchoolDXD = "High-School-DXD"
    Simulation = "Simulation"
    HunterXHunter = "Hunter-X-Hunter"
    Reincarnation = "Reincarnation"
    Cartoonist = "Cartoonist"
    Doomsday = "Doomsday"
    Urban = "Urban"
    Doraemon = "Doraemon"
    ThreeKingdoms = "Three-Kingdoms"
    Daqin = "Daqin"
    Entertainment = "Entertainment"
    NBA = "NBA"
    TombRaider = "Tomb-Raider"
    GlobalReincarnation = "Global-Reincarnation"
    DragonBall = "Dragon-Ball"
    Comprehensive = "Comprehensive"
    LiveBroadcast = "Live-Broadcast"
    Store = "Store"
    Horror = "Horror"
    Siheyuan = "Siheyuan"
    Zombie = "Zombie"
    Ultraman = "Ultraman"
    Survival = "Survival"
    HongKong = "Hong-Kong"
    Football = "Football"
    Tennis = "Tennis"
    YugiOh = "Yugi-Oh"
    Bleach = "Bleach"
    Detective = "Detective"
    LeagueOfLegends = "League-Of-Legends"
    DemonSlayer = "Demon-Slayer"
    ShokugekiNoSoma = "Shokugeki-No-Soma"
    Rebirth = "Rebirth"
    System = "System"
    Teacher = "Teacher"
    InvincibleFlow = "Invincible-Flow"
    JackieChan = "Jackie-Chan"
    ChinaDynasty = "China-Dynasty"
    Technology = "Technology"
    JourneyToTheWest = "Journey-To-The-West"
    OnePunchMan = "One-Punch-Man"
    SpecialForces = "Special-Forces"
    R18 = "R18"
    Uncategorised = "Uncategorised"

    @classmethod
    def from_string(cls, string: str) -> str:
        for category in cls:
            if any(term.lower() in string.lower() for term in getattr(Aliases, category.name).value):
                return category.name
        return cls.Uncategorised.name

    @classmethod
    def get_tags_from_string(cls, string: str) -> list[str]:
        tags = []
        for category in cls:
            for term in getattr(Aliases, category.name).value:
                if term.lower() in string.lower():
                    tags.append(category.name)
        return tags

    @classmethod
    def all_tags(cls) -> list[str]:
        tags: list[str] = []
        for category in cls:
            tags.extend(getattr(Aliases, category.name).value)
        return tags


class Aliases(enum.Enum):
    Naruto = [
        "naruto",
        "konoha",
        "hokage",
        "火影",
        "木叶",
        "cloud vill",
        "云隐村",
        "uchiha",
        "宇智波",
        "orochimaru",
        "tsunade",
        "indra",
        "chakra",
        "ninja",
        "nine tails",
        "kushina",
        "minato",
        "tailed beast",
        "tail beast",
    ]
    OnePiece = [
        "one piece",
        "海贼",
        "onepiece",
        "one-piece",
        "one_piece",
        "pirate",
        "白胡子",
        "white beard",
        "big mom",
        "柱灭之刃",
        "big-mom",
        "kaido",
        "charlotte",
        "nami",
        "robin",
        "grand voyage",
        "great voyage",
        "akainu",
        "yellow ape",
        "navy",
        "celestial dragon",
        "great route",
    ]
    Marvel = ["marvel", "meimen", "infinite gem", "loki", "thor", "shield agent", "coulson", "agent shield"]
    DC = ["superman", "bat-man", "super-man", "clark", "speedster", "aquaman"]
    HarryPotter = ["Harry-Potter", "Harry-Potter-World", "Harry-Potter-World-2"]
    Pokemon = ["pokemon", "神奇宝贝", "精灵", "elves", "elf", "trainer", "digimon", "pokémon"]
    ChatRoom = [
        "聊天群组",
        "聊天室",
        "chat group",
        "chat rooms",
        "chatgroup",
        "red envelope",
        "exchange group",
        "exchangegroup",
    ]
    Villain = ["villain", "hunt protagonist"]
    SpiritRecovery = ["reiki", "灵气复苏", "诡异复苏", "aura", "spirit rec", "recovery", "灵级复苏"]
    Fantasy = ["fantasy", "玄幻", "xuanhuan", "wuxia", "wu xia", "tame", "evolve", "evolution", "empress", "cultivation"]
    FairyTail = [
        "fairy tail",
        "妖尾",
        "erza",
        "meera",
    ]
    GenshinImpact = ["genshin", "原神"]
    DoulouDaluo = ["douluo", "斗罗", "spirit ring", "spiritring", "tan san"]
    PreHistoric = ["flood", "prehistoric", "honghuang", "洪荒", "nuwa", "nezha"]
    OnlineGames = ["player", "online game", "网游", "npc", "game", "online", "onlinegame"]
    Conan = ["conan", "winery", "belmod", "belmod", "black organization", "blackorganization"]
    HighSchoolDXD = ["high school", "dxd", "惡魔高校", "demon high"]
    Simulation = ["simulation", "模拟"]
    HunterXHunter = ["hunter", "猎人", "hunterXhunter", "hxh"]
    Reincarnation = ["全球综漫轮", "global reincarnation", "global", "spiritual energy"]
    Cartoonist = ["animation", "manga", "cartoonist", "writer", "级漫画家", "画家", "anime"]
    Doomsday = ["doomsday", "apocalypse"]
    Urban = ["urban", "city", "shenhao", "school flower", "doctor"]
    Doraemon = ["doraemon", "nobita", "shizuka"]
    ThreeKingdoms = ["three kingdom", "3 king", "threekingdom", "threekingdoms"]
    Daqin = ["daqin", "datang"]
    Entertainment = ["entertainment", "actor", "film and television"]
    NBA = ["nba", "basketball"]
    TombRaider = ["tomb raider", "tombraider", "tomb"]
    GlobalReincarnation = ["全球综漫轮", "global reincarnation", "global", "spiritual energy"]
    DragonBall = ["龙珠", "dragon ball", "trunks", "goku", "vegeta", "vegito", "破坏神", "god of destruction"]
    Comprehensive = ["dimensional", "综漫", "comprehensive", "anime"]
    LiveBroadcast = ["live broadcast", "broadcast", "anchor", "stream"]
    Store = ["shop", "store"]
    Horror = ["thriller", "horror", "terror", "horror", "terrorist"]
    Siheyuan = ["siheyuan"]
    Zombie = ["zombie", "ninth uncle"]
    Ultraman = ["ultraman", "ott", "dagu"]
    Survival = ["survival", "ice age", "desert", "island"]
    HongKong = ["survival", "ice age", "desert", "island"]
    Football = ["football"]
    Tennis = ["tennis", "prince of tennis"]
    YugiOh = ["card", "yu-gi-oh", "yugio"]
    Bleach = ["zanpakuto", "bleach", "gotei", "reaper"]
    Detective = ["detective"]
    LeagueOfLegends = ["lol", "arcane", "jinx", "league"]
    DemonSlayer = ["柱灭之刃", "slayer", "demonslayer"]
    ShokugekiNoSoma = ["shokugeki", "halberd", "erina", "totsuki", "food war"]
    Rebirth = ["rebirth", "reincarnation", "re-incarnation", "重生"]
    System = ["system", "系统"]
    Teacher = ["teacher", "老师"]
    InvincibleFlow = ["invincible", "最强", "strong", "god level", "god-level"]
    JackieChan = ["jackie"]
    ChinaDynasty = ["tang", "dynasty", "song dy"]
    Technology = ["tech", "robot", "scholar", "satellite", "study", "invent", "build", "scientific", "research"]
    JourneyToTheWest = [
        "journey to west",
        "monkey king",
        "journey to the west",
        "west journey",
        "westward journey",
        "wuzhu",
    ]
    OnePunchMan = ["saitama", "one punch", "onepunch", "genos"]
    SpecialForces = ["special force", "agent"]
    R18 = ["sex", "horny", "incest", "busty", "r18", "fuck", "hynosis", "rape"]
    Uncategorised = ["uncategorised"]
