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
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055447337369096222/image0.jpg",
            "https://img.webnovel.com/bookcover/18637939706581305/180/180.jpg?updateTime=1606424740185",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055497145437925436/image0.jpg",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055497231756689418/image0.jpg",
        ],
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
        thumbnails=[
            "https://m.media-amazon.com/images/M/MV5BODcwNWE3OTMtMDc3MS00NDFjLWE1OTAtNDU3NjgxODMxY2UyXk"
            "EyXkFqcGdeQXVyNTAyODkwOQ@@._V1_.jpg",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055496831985008671/image0.jpg",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055496965691027496/image0.jpg",
        ],
    )
    Marvel = Category(
        name="Marvel",
        tags=["marvel", "meimen", "infinite gem", "loki", "shield agent", "coulson", "agent shield"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055497322953441360/image0.jpg",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055497401269502032/image0.jpg",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055497401269502032/image0.jpg",
        ],
    )
    DC = Category(
        name="DC",
        tags=["superman", "bat-man", "super-man", "clark", "speedster", "aquaman"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055497580416610385/image0.jpg",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055497831110152223/image0.jpg",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055497963570479156/image0.jpg",
        ],
    )
    HarryPotter = Category(
        name="Harry-Potter",
        tags=["harry potter", "hogwarts", "harry", "potter", "hermione", "ron", "draco", "dumbledore", "voldemort"],
        thumbnails=[
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS26O29WU8eOxVEVaH7lmNQK28oAi7rqeBN7g&usqp=CAU",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1056116267259535392/2Q.png",
        ],
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
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055686344292179968/images.png",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055686587318538260/images.png",
        ],
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
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055686132173639730/2Q.png",
        ],
    )
    Villain = Category(
        name="Villain",
        tags=["villain", "hunt protagonist"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055685768997240923/images.png",
        ],
    )
    SpiritRecovery = Category(
        name="Spirit-Recovery",
        tags=["reiki", "灵气复苏", "诡异复苏", "aura", "spirit rec", "recovery", "灵级复苏", "Rejuvenation"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055491892336406568/image0.jpg",
        ],
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
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055493329741160498/image0.jpg",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055493927328825344/image0.jpg",
        ],
    )
    FairyTail = Category(
        name="Fairy-Tail",
        tags=["fairy tail", "妖尾", "erza", "meera", "gray", "natsu", "lucy", "fairytail", "fairy-tail", "dragon slayer"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055671200258473994/MV5BMzZjNmRhNWQ"
            "tNTAyYy00Yjk2LWE0NzUtMmYyNTU0YTE5NjJiXkEyXkFqcGdeQXVyNjI4OTE5OTM._V1_FMjpg_UX1000_.jpg",
        ],
    )
    GenshinImpact = Category(
        name="Genshin-Impact",
        tags=["genshin", "原神"],
        thumbnails=["https://cdn.discordapp.com/attachments/1055445441958916167/1055685539338133625/Z.png"],
    )
    DoulouDaluo = Category(
        name="Doulou-Daluo",
        tags=["douluo", "斗罗", "spirit ring", "spiritring", "tan san"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055685388116692992/9k.png",
        ],
    )
    PreHistoric = Category(
        name="Pre-Historic",
        tags=["flood", "prehistoric", "honghuang", "洪荒", "nuwa", "nezha"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055685179986935828/Z.png",
        ],
    )
    OnlineGames = Category(
        name="Online-Games",
        tags=["player", "online game", "网游", "npc", "game", "online", "onlinegame"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055684931474432101/9k.png",
        ],
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
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055671107396567061/MV5"
            "BMzA1MmI0OGItODU3NS00ZTA0LWI2OTMtYjMyZDVmNjI2YzdlXkEyXkFqcGdeQXVyMTA0MTM5NjI2._V1_.jpg",
        ],
    )
    HighSchoolDXD = Category(
        name="High-School-DXD",
        tags=["high school", "dxd", "惡魔高校", "demon high"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055493913852530718/image0.jpg",
        ],
    )
    Simulation = Category(
        name="Simulation",
        tags=["simulation", "模拟", "模拟人生", "life simulation", "life", "simulator", "sim", "simulation game"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055684669192015902/Z.png",
        ],
    )
    HunterXHunter = Category(
        name="Hunter-X-Hunter",
        tags=["hunter", "猎人", "hunterXhunter", "hxh"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055684394603520000/Z.png",
        ],
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
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055491353162821722/image0.jpg",
        ],
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
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055684274113749042/images.png",
        ],
    )
    Doomsday = Category(
        name="Doomsday",
        tags=["doomsday", "apocalyps", "survival"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055683758201774190/9k.png",
        ],
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
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055683652605984800/2Q.png",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055740537648451624/Scifi.jpg",
        ],
    )
    Doraemon = Category(
        name="Doraemon",
        tags=["doraemon", "nobita", "shizuka"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055671305577435176/MV"
            "5BMGIzZmQ4YmUtZGQ4NC00OTkyLWE1MGUtMTQ3N2Y3N2E2NWEyXkEyXkFqcGdeQXVyODAzNzAwOTU._V1_FMjpg_UX1000_.jpg",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1056119315256053861/images.png",
        ],
    )
    ThreeKingdoms = Category(
        name="Three-Kingdoms",
        tags=["three kingdom", "3 king", "threekingdom", "threekingdoms"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055495631097045042/image0.png",
        ],
    )
    Daqin = Category(
        name="Daqin",
        tags=["daqin", "datang"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055683421759868938/Z.png",
        ],
    )
    Entertainment = Category(
        name="Entertainment",
        tags=["entertainment", "娱乐", "actor", "film and television"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055683217824436254/Z.png",
        ],
    )
    NBA = Category(
        name="NBA",
        tags=["nba", "basketball"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055682899833278475/2Q.png",
        ],
    )
    TombRaider = Category(
        name="Tomb-Raider",
        tags=["tomb raider", "tombraider", "tombraiders", "tomb"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055682789372076082/2Q.png",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055683983918239744/FB_IMG_1671763662541.jpg",
        ],
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
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055682618751983688/images.png",
        ],
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
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055682176911417394/images.png",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055682261456007168/images.png",
        ],
    )
    Comprehensive = Category(
        name="Comprehensive",
        tags=["dimensional", "综漫", "comprehensive", "anime"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055681961944961144/2Q.png",
        ],
    )
    LiveBroadcast = Category(
        name="Live-Broadcast",
        tags=["live broadcast", "broadcast", "anchor", "stream"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055681682927255674/images.png",
        ],
    )
    Store = Category(
        name="Store",
        tags=["store", "商店", "shop", "shopping"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055495985587032124/image0.jpg",
        ],
    )
    Horror = Category(
        name="Horror",
        tags=["thriller", "horror", "terror", "horror", "terrorist"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055680954791907348/Z.png",
        ],
    )
    Siheyuan = Category(
        name="Siheyuan",
        tags=["siheyuan"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055680864710840481/images.png",
        ],
    )
    Zombie = Category(
        name="Zombie",
        tags=["zombie", "ninth uncle"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055680643276755004/9k.png",
        ],
    )
    Ultraman = Category(
        name="Ultraman",
        tags=["ultraman", "ott", "dagu"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055680491405189302/images.png",
        ],
    )
    Survival = Category(
        name="Survival",
        tags=["survival", "ice age", "desert", "island", "wilderness"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055680246168424638/9k.png",
        ],
    )
    HongKong = Category(
        name="Hong-Kong",
        tags=["hongkong", "hong kong"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055679879116496957/images.png",
        ],
    )
    Football = Category(
        name="Football",
        tags=["football"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055679346498617374/2Q.png",
        ],
    )
    Tennis = Category(
        name="Tennis",
        tags=["tennis", "prince of tennis"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055679612346179674/2Q.png",
        ],
    )
    YugiOh = Category(
        name="Yugi-Oh",
        tags=["card", "yu-gi-oh", "yugio"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055495465333948496/image0.jpg",
        ],
    )
    Bleach = Category(
        name="Bleach",
        tags=[
            "zanpakuto",
            "bleach",
            "gotei",
            "reaper",
            "Shinigami",
            "reiatsu",
            "liuhun street",
            "aizen",
            "hueco mundo",
        ],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055671586537095239/Bleachanime.png",
        ],
    )
    Detective = Category(
        name="Detective",
        tags=["detective", "investigation", "investigator", "investigate", "investigation"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055679191644909678/Z.png",
        ],
    )
    LeagueOfLegends = Category(
        name="League-Of-Legends",
        tags=["lol", "arcane", "jinx", "league"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055678998857924699/Z.png",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055739801833328690/Classic.jpg",
        ],
    )
    DemonSlayer = Category(
        name="Demon-Slayer",
        tags=["柱灭之刃", "slayer", "demonslayer"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055493148043923466/image0.jpg",
        ],
    )
    ShokugekiNoSoma = Category(
        name="Shokugeki-No-Soma",
        tags=["shokugeki", "halberd", "erina", "totsuki", "food war"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055491408661844009/image0.jpg",
        ],
    )
    Rebirth = Category(
        name="Rebirth",
        tags=["rebirth", "reincarnation", "re-incarnation", "重生"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055678594346659901/images.png",
        ],
    )
    System = Category(
        name="System",
        tags=["system", "系统"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055672186167377970/Z.png",
        ],
    )
    Teacher = Category(
        name="Teacher",
        tags=["teacher", "教师"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055678247733567548/9k.png",
        ],
    )
    InvincibleFlow = Category(
        name="Invincible-Flow",
        tags=["invincible", "无敌流", "invincible", "最强", "strong", "god level", "god-level"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055677779791855626/Z.png",
        ],
    )
    JackieChan = Category(
        name="Jackie-Chan",
        tags=["jackie chan", "成龙", "jackie", "chan"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055672684211622002/9k.png",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055672780772880494/2Q.png",
        ],
    )
    ChinaDynasty = Category(
        name="China-Dynasty",
        tags=["tang", "dynasty", "song dy"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055494594495791104/image0.jpg",
        ],
    )
    Technology = Category(
        name="Technology",
        tags=["tech", "robot", "scholar", "satellite", "study", "invent", "build", "scientific", "research"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055672382133633085/images.png",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055672486198530191/9k.png",
        ],
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
        thumbnails=[
            "https://cdn.theworldofchinese.com/media/images/monkey-master.original.jpg",
        ],
    )
    OnePunchMan = Category(
        name="One-Punch-Man",
        tags=["saitama", "one punch", "onepunch", "genos"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055494445799321702/image0.jpg",
        ],
    )
    SpecialForces = Category(
        name="Special-Forces",
        tags=["special force", "agent"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055671253807149096/9k.png",
        ],
    )
    R18 = Category(
        name="R18",
        tags=["sex", "horny", "incest", "busty", "r18", "fuck", "hynosis", "rape"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055493803848519771/FB_IMG_1671010145233.jpg",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055669249311518812/small29"
            "08898de22cda09d2db9dff75cae8d31670486759.png",
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055669343238770738/smallfdb07a"
            ">8a192500ff3d42753a960617da1671097309.png",
        ],
    )
    Uncategorised = Category(
        name="Uncategorised",
        tags=["uncategorised"],
        thumbnails=[
            "https://cdn.discordapp.com/attachments/1055445441958916167/1055780604655964210/image0.jpg",
        ],
    )

    @classmethod
    def thumbnail_from_category(cls, string: str) -> str:
        for category in cls:
            if category.value.name == string:
                return random.choice(category.value.thumbnails)
        return ""

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
