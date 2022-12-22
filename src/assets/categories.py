import dataclasses
import enum
import random

__all__: tuple[str, ...] = ("Categories",)


@dataclasses.dataclass
class Category:
    name: str
    tags: list[str]
    thumbnails: list[str]


class Categories(enum.Enum):
    Naruto = Category(
        name="Naruto",
        tags=[
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
        ],
        thumbnails=[],
    )
    OnePiece = Category(
        name="One-Piece",
        tags=[
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
        ],
        thumbnails=[],
    )
    Marvel = Category(
        name="Marvel",
        tags=["marvel", "meimen", "infinite gem", "loki", "thor", "shield agent", "coulson", "agent shield"],
        thumbnails=[],
    )
    DC = Category(name="DC", tags=["superman", "bat-man", "super-man", "clark", "speedster", "aquaman"], thumbnails=[])
    HarryPotter = Category(
        name="Harry-Potter",
        tags=["harry potter", "hogwarts", "harry", "potter", "hermione", "ron", "draco", "dumbledore", "voldemort"],
        thumbnails=[],
    )
    Pokemon = Category(
        name="Pokemon",
        tags=[
            "pokemon",
            "pikachu",
            "ash",
            "misty",
            "brock",
            "gym leader",
            "gym",
            "pokémon",
            "神奇宝贝",
            "精灵",
            "elves",
            "elf",
            "trainer",
            "digimon",
            "pokémon",
        ],
        thumbnails=[],
    )
    ChatRoom = Category(
        name="Chat-Room",
        tags=[
            "聊天群组",
            "聊天室",
            "chat group",
            "chat rooms",
            "chatgroup",
            "red envelope",
            "exchange group",
            "exchangegroup",
        ],
        thumbnails=[],
    )
    Villain = Category(name="Villain", tags=["villain", "hunt protagonist"], thumbnails=[])
    SpiritRecovery = Category(
        name="Spirit-Recovery", tags=["reiki", "灵气复苏", "诡异复苏", "aura", "spirit rec", "recovery", "灵级复苏"], thumbnails=[]
    )
    Fantasy = Category(
        name="Fantasy",
        tags=[
            "fantasy",
            "魔法",
            "magic",
            "wizard",
            "玄幻",
            "xuanhuan",
            "wuxia",
            "wu xia",
            "tame",
            "evolve",
            "evolution",
            "empress",
            "cultivation",
        ],
        thumbnails=[],
    )
    FairyTail = Category(
        name="Fairy-Tail",
        tags=["fairy tail", "妖尾", "erza", "meera", "gray", "natsu", "lucy", "fairytail", "fairy-tail", "dragon slayer"],
        thumbnails=[],
    )
    GenshinImpact = Category(name="Genshin-Impact", tags=["genshin", "原神"], thumbnails=[])
    DoulouDaluo = Category(
        name="Doulou-Daluo", tags=["douluo", "斗罗", "spirit ring", "spiritring", "tan san"], thumbnails=[]
    )
    PreHistoric = Category(
        name="Pre-Historic",
        tags=["flood", "prehistoric", "honghuang", "洪荒", "nuwa", "nezha"],
        thumbnails=[],
    )
    OnlineGames = Category(
        name="Online-Games",
        tags=["player", "online game", "网游", "npc", "game", "online", "onlinegame"],
        thumbnails=[],
    )
    Conan = Category(
        name="Conan",
        tags=[
            "conan",
            "shinichi",
            "kudo",
            "kaito",
            "winery",
            "belmod",
            "belmod",
            "black organization",
            "blackorganization",
        ],
        thumbnails=[],
    )
    HighSchoolDXD = Category(
        name="High-School-DXD",
        tags=["high school", "dxd", "惡魔高校", "demon high"],
        thumbnails=[],
    )
    Simulation = Category(
        name="Simulation",
        tags=["simulation", "模拟", "模拟人生", "life simulation", "life", "simulator", "sim", "simulation game"],
        thumbnails=[],
    )
    HunterXHunter = Category(
        name="Hunter-X-Hunter",
        tags=["hunter", "猎人", "hunterXhunter", "hxh"],
        thumbnails=[],
    )
    Reincarnation = Category(
        name="Reincarnation",
        tags=[
            "reincarnation",
            "转生",
            "reincarnate",
            "reincarnated",
            "全球综漫轮",
            "global reincarnation",
            "global",
            "spiritual energy",
        ],
        thumbnails=[],
    )
    Cartoonist = Category(
        name="Cartoonist",
        tags=[
            "cartoonist",
            "漫画家",
            "cartoon",
            "comics",
            "comic",
            "comic artist",
            "animation",
            "manga",
            "cartoonist",
            "writer",
            "级漫画家",
            "画家",
            "anime",
        ],
        thumbnails=[],
    )
    Doomsday = Category(
        name="Doomsday",
        tags=["doomsday", "apocalyps", "survival"],
        thumbnails=[],
    )
    Urban = Category(
        name="Urban",
        tags=[
            "urban",
            "都市",
            "city",
            "urban fantasy",
            "urban fantasy",
            "urban",
            "city",
            "shenhao",
            "school flower",
            "doctor",
        ],
        thumbnails=[],
    )
    Doraemon = Category(
        name="Doraemon",
        tags=["doraemon", "nobita", "shizuka"],
        thumbnails=[],
    )
    ThreeKingdoms = Category(
        name="Three-Kingdoms",
        tags=["three kingdom", "3 king", "threekingdom", "threekingdoms"],
        thumbnails=[],
    )
    Daqin = Category(
        name="Daqin",
        tags=["daqin", "datang"],
        thumbnails=[],
    )
    Entertainment = Category(
        name="Entertainment",
        tags=["entertainment", "娱乐", "actor", "film and television"],
        thumbnails=[],
    )
    NBA = Category(
        name="NBA",
        tags=["nba", "basketball"],
        thumbnails=[],
    )
    TombRaider = Category(
        name="Tomb-Raider",
        tags=["tomb raider", "tombraider", "tombraiders", "tomb"],
        thumbnails=[],
    )
    GlobalReincarnation = Category(
        name="Global-Reincarnation",
        tags=[
            "global reincarnate",
            "global reincarnated",
            "global",
            "全球综漫轮",
            "global reincarnation",
            "global",
            "spiritual energy",
        ],
        thumbnails=[],
    )
    DragonBall = Category(
        name="Dragon-Ball",
        tags=[
            "dragonball",
            "db",
            "dbz",
            "dragonballz",
            "dragonballsuper",
            "dragonball super",
            "dragonballgt",
            "dragonball gt",
            "龙珠",
            "dragon ball",
            "trunks",
            "goku",
            "vegeta",
            "vegito",
            "破坏神",
            "god of destruction",
        ],
        thumbnails=[],
    )
    Comprehensive = Category(
        name="Comprehensive",
        tags=["dimensional", "综漫", "comprehensive", "anime"],
        thumbnails=[],
    )
    LiveBroadcast = Category(
        name="Live-Broadcast",
        tags=["live broadcast", "broadcast", "anchor", "stream"],
        thumbnails=[],
    )
    Store = Category(
        name="Store",
        tags=["store", "商店", "shop", "shopping"],
        thumbnails=[],
    )
    Horror = Category(
        name="Horror",
        tags=["thriller", "horror", "terror", "horror", "terrorist"],
        thumbnails=[],
    )
    Siheyuan = Category(
        name="Siheyuan",
        tags=["siheyuan"],
        thumbnails=[],
    )
    Zombie = Category(
        name="Zombie",
        tags=["zombie", "ninth uncle"],
        thumbnails=[],
    )
    Ultraman = Category(
        name="Ultraman",
        tags=["ultraman", "ott", "dagu"],
        thumbnails=[],
    )
    Survival = Category(
        name="Survival",
        tags=["survival", "ice age", "desert", "island"],
        thumbnails=[],
    )
    HongKong = Category(
        name="Hong-Kong",
        tags=["hongkong", "hong kong"],
        thumbnails=[],
    )
    Football = Category(
        name="Football",
        tags=["football"],
        thumbnails=[],
    )
    Tennis = Category(
        name="Tennis",
        tags=["tennis", "prince of tennis"],
        thumbnails=[],
    )
    YugiOh = Category(
        name="Yugi-Oh",
        tags=["card", "yu-gi-oh", "yugio"],
        thumbnails=[],
    )
    Bleach = Category(
        name="Bleach",
        tags=["zanpakuto", "bleach", "gotei", "reaper"],
        thumbnails=[],
    )
    Detective = Category(
        name="Detective",
        tags=["detective", "investigation", "investigator", "investigate", "investigation"],
        thumbnails=[],
    )
    LeagueOfLegends = Category(
        name="League-Of-Legends",
        tags=["lol", "arcane", "jinx", "league"],
        thumbnails=[],
    )
    DemonSlayer = Category(
        name="Demon-Slayer",
        tags=["柱灭之刃", "slayer", "demonslayer"],
        thumbnails=[],
    )
    ShokugekiNoSoma = Category(
        name="Shokugeki-No-Soma",
        tags=["shokugeki", "halberd", "erina", "totsuki", "food war"],
        thumbnails=[],
    )
    Rebirth = Category(
        name="Rebirth",
        tags=["rebirth", "reincarnation", "re-incarnation", "重生"],
        thumbnails=[],
    )
    System = Category(
        name="System",
        tags=["system", "系统"],
        thumbnails=[],
    )
    Teacher = Category(
        name="Teacher",
        tags=["teacher", "教师"],
        thumbnails=[],
    )
    InvincibleFlow = Category(
        name="Invincible-Flow",
        tags=["invincible", "无敌流", "invincible", "最强", "strong", "god level", "god-level"],
        thumbnails=[],
    )
    JackieChan = Category(
        name="Jackie-Chan",
        tags=["jackie chan", "成龙", "jackie", "chan"],
        thumbnails=[],
    )
    ChinaDynasty = Category(
        name="China-Dynasty",
        tags=["tang", "dynasty", "song dy"],
        thumbnails=[],
    )
    Technology = Category(
        name="Technology",
        tags=["tech", "robot", "scholar", "satellite", "study", "invent", "build", "scientific", "research"],
        thumbnails=[],
    )
    JourneyToTheWest = Category(
        name="Journey-To-The-West",
        tags=[
            "journey to west",
            "monkey king",
            "journey to the west",
            "west journey",
            "westward journey",
            "wuzhu",
        ],
        thumbnails=[],
    )
    OnePunchMan = Category(
        name="One-Punch-Man",
        tags=["saitama", "one punch", "onepunch", "genos"],
        thumbnails=[],
    )
    SpecialForces = Category(
        name="Special-Forces",
        tags=["special force", "agent"],
        thumbnails=[],
    )
    R18 = Category(
        name="R18",
        tags=["sex", "horny", "incest", "busty", "r18", "fuck", "hynosis", "rape"],
        thumbnails=[],
    )
    Uncategorised = Category(
        name="Uncategorised",
        tags=["uncategorised"],
        thumbnails=[],
    )

    @classmethod
    def thumbnail_from_category(cls, string: str) -> str:
        for category in cls:
            if category.value.name == string:
                return random.choice(category.value.thumbnails)

    @classmethod
    def from_string(cls, string: str) -> str:
        for category in cls:
            if any(term.lower() in string.lower() for term in category.value.tags):
                return category.value.name
        return cls.Uncategorised.name

    @classmethod
    def get_tags_from_string(cls, string: str) -> list[str]:
        tags = []
        for category in cls:
            for term in category.value.tags:
                if term.lower() in string.lower():
                    tags.append(category.value.name)
        return tags

    @classmethod
    def all_tags(cls) -> list[str]:
        tags: list[str] = []
        for category in cls:
            tags.extend(category.value.tags)
        return tags
