class Categorizer:
    CAT = ["Naruto", "One-piece", "Marvel", "DC", "Pokemon", "Chat-room", "Villain", "Spirit-recovery",
           "Fantasy", "Fairy-tail", "Genshin", "Douluo", "Pre-historic", "Online-Games",
           "Conan", "High School dxd", "Simulation", "Hunter X Hunter", "Cartoonist", "Doomsday",
           "Urban", "Doraemon", "Three kingdom", "Daqin", "Entertainment", "NBA", "Tomb raider", "Harry Potter",
           "Global reincarnation", "Dragon ball", "Comprehensive", "Live Broadcast",
           "store", "horror", "Siheyuan", "Zombie", "Ultraman", "survival", "Hong Kong",
           "football", "tennis", "anti-japanese", "yugi-oh", "bleach", "detective", "LOL", "demon slayer",
           "shokugeki", "rebirth", "system", "Teacher", "Invincible flow",
           "Jackie chan", "China dynasty", "Tech", "Journey to west", "One-punch man", "Special forces", "uncategorized", "others"]

    @staticmethod
    def get_categories():
        CAT = ["Naruto", "One-piece", "Marvel", "DC", "Pokemon", "Chat-room", "Villain", "Spirit-recovery",
               "Fantasy", "Fairy-tail", "Genshin", "Douluo", "Pre-historic", "Online-Games",
               "Conan", "High School dxd", "Simulation", "Hunter X Hunter", "Cartoonist", "Doomsday",
               "Urban", "Doraemon", "Three kingdom", "Daqin", "Entertainment", "NBA", "Tomb raider", "Harry Potter",
               "Global reincarnation", "Dragon ball", "Comprehensive", "Live Broadcast",
               "store", "horror", "Siheyuan", "Zombie", "Ultraman", "survival", "Hong Kong",
               "football", "tennis", "anti-japanese", "yugi-oh", "bleach", "detective", "LOL", "demon slayer",
               "shokugeki", "rebirth", "system", "Teacher", "Invincible flow",
               "Jackie chan", "China dynasty", "Tech", "Journey to west", "One-punch man", "Special forces", "uncategorized", "others"]

        return CAT

    async def find_category(self, file_name):
        naruto = ['naruto', 'konoha', 'hokage', '火影', '木叶', 'cloud vill', '云隐村', 'uchiha', '宇智波', 'orochimaru',
                  'tsunade', 'indra', 'chakra', 'ninja', 'nine tails', 'kushina', 'minato', 'tailed beast',
                  'tail beast']
        onepiece = ['one piece', '海贼', 'onepiece', 'one-piece', 'one_piece', 'pirate', '白胡子', 'white beard',
                    'big mom', '柱灭之刃', 'big-mom', 'kaido', 'charlotte', 'nami', 'robin', 'grand voyage',
                    'great voyage', 'akainu', 'yellow ape', 'navy', 'celestial dragon', 'great route']
        dc = ['superman', 'bat-man', 'super-man', 'clark', 'speedster', 'aquaman']
        marvel = ['marvel', 'meimen', '美漫', '漫威', 'infinite gem', 'loki', 'thor', 'shield agent', 'coulson', 'agent shield']
        pokemon = ['pokemon', '神奇宝贝', '精灵', 'elves', 'elf', 'trainer', 'digimon', 'pokémon']
        chatroom = ['聊天群组', '聊天室', 'chat group', 'chat rooms', 'chatgroup',
                    'red envelope', 'exchange group', 'exchangegroup']
        villain = ['villain', '反派']
        spiritrecovery = ['reiki', '灵气复苏', '诡异复苏', 'aura', 'spirit rec', 'recovery', '灵级复苏']
        fantasy = ['fantasy', '玄幻', 'xuanhuan', 'wuxia', 'wu xia', 'tame', 'evolve', 'evolution', 'empress',
                   'cultivation']
        fairytail = ['fairy tail', '妖尾', 'erza', 'meera', ]
        genshin = ['genshin', '原神']
        douluo = ['douluo', '斗罗', 'spirit ring', 'spiritring', 'tan san']
        prehistoric = ['flood', 'prehistoric', 'honghuang', '洪荒', 'nuwa', 'nezha']
        onlinegames = ['player', 'online game', '网游', 'npc', 'game', 'online', 'onlinegame']
        conan = ['conan', 'winery', 'belmod', 'belmod', 'black organization', 'blackorganization']
        highdxd = ['high school', 'dxd', '惡魔高校', 'demon high']
        simulation = ['simulation', '模拟']
        hunter = ['hunter', '猎人', 'hunterXhunter', 'hxh']
        globalrei = ['全球综漫轮', 'global reincarnation', 'global', 'spiritual energy']
        dragonball = ['龙珠', 'dragon ball', 'trunks', 'goku', 'vegeta', 'vegito', '破坏神', 'god of destruction']
        comprehensive = ['dimensional', '综漫', 'comprehensive', 'anime']
        livebroadcast = ['live broadcast', '直播', 'broadcast', 'anchor', 'stream']
        cartoonist = ['animation', 'manga', 'cartoonist', 'writer', '级漫画家', '画家', 'anime']
        doomsday = ['doomsday', '毁灭', 'apocalypse']
        urban = ['urban', 'city', '都市', '都市', 'shenhao', 'school flower', 'doctor']
        doraemon = ['doraemon', 'nobita', 'shizuka']
        threeking = ['three kingdom', '3 king', 'threekingdom', 'threekingdoms']
        daqin = ['daqin', 'datang']
        entertainment = ['entertainment', 'actor', 'film and tele']
        nba = ['nba', 'basketball']
        tombraider = ['tomb raider', 'tombraider', 'tomb']
        harry = ['harry', 'potter', 'hermoine', 'hogwarts', 'dumbledore', 'albus']
        shop = ['shop', 'store']
        thriller = ['thriller', 'horror', 'terror', 'horror', 'terrorist']
        Siheyuan = ['Siheyuan']
        ultraman = ['ultraman', 'ott', 'dagu']
        zombie = ['zombie', 'ninth uncle']
        survival = ['survival', 'ice age', 'desert', 'island']
        hongkong = ['hongkong', 'hong kong']
        football = ['football']
        tennis = ['tennis', 'prince of tennis']
        antijp = ['anti-japanese', 'anti japanese']
        ygo = ['card', 'yu-gi-oh', 'yugio']
        bleach = ['zanpakuto', 'bleach', 'gotei', 'reaper']
        detective = ['detective']
        leagueoflegends = ['lol', 'arcane', 'jinx', 'league']
        demonslayer = ['柱灭之刃', 'slayer', 'demonslayer']
        shokugeki = ['shokugeki', 'halberd', 'erina', 'totsuki', 'food war']
        rebirth = ['rebirth', 'reincarnation', 're-incarnation', '重生']
        system = ['system', '系统']
        teacher = ['teacher', '老师']
        invincible = ['invinc', '最强', 'strong', "god level", "god-level"]
        jackie = ['jackie', '成龙']
        dynasty = ['tang', 'dynasty', 'song dy']
        tech = ['tech', 'robot', 'scholar', 'satellite', 'study', 'invent', 'build', 'scientific', 'research']
        journey2west = ['journey to west', 'monkey king', 'journey to the west', 'west journey', 'westward journey',
                        'wuzhu']
        onepunch = ['saitama', 'one punch', 'onepunch', 'genos']
        specialforces = ['special force', 'agent']

        if any(term in file_name.lower() for term in naruto):
            return "Naruto"
        elif any(term in file_name.lower() for term in onepiece):
            return "One-piece"
        elif any(term in file_name.lower() for term in marvel):
            return "Marvel"
        elif any(term in file_name.lower() for term in dc):
            return "DC"
        elif any(term in file_name.lower() for term in onlinegames):
            return "Online-Games"
        elif any(term in file_name.lower() for term in pokemon):
            return "Pokemon"
        elif any(term in file_name.lower() for term in chatroom):
            return "Chat-room"
        elif any(term in file_name.lower() for term in villain):
            return "Villain"
        elif any(term in file_name.lower() for term in spiritrecovery):
            return "Spirit-recovery"
        elif any(term in file_name.lower() for term in fantasy):
            return "Fantasy"
        elif any(term in file_name.lower() for term in fairytail):
            return "Fairy-tail"
        elif any(term in file_name.lower() for term in genshin):
            return "Genshin"
        elif any(term in file_name.lower() for term in douluo):
            return "Douluo"
        elif any(term in file_name.lower() for term in prehistoric):
            return "Pre-historic"
        elif any(term in file_name.lower() for term in conan):
            return "Conan"
        elif any(term in file_name.lower() for term in highdxd):
            return "High School dxd"
        elif any(term in file_name.lower() for term in simulation):
            return "Simulation"
        elif any(term in file_name.lower() for term in hunter):
            return "Hunter X Hunter"
        elif any(term in file_name.lower() for term in cartoonist):
            return "Cartoonist"
        elif any(term in file_name.lower() for term in doomsday):
            return "Doomsday"
        elif any(term in file_name.lower() for term in urban):
            return "Urban"
        elif any(term in file_name.lower() for term in doraemon):
            return "Doraemon"
        elif any(term in file_name.lower() for term in threeking):
            return "Three kingdom"
        elif any(term in file_name.lower() for term in daqin):
            return "Daqin"
        elif any(term in file_name.lower() for term in entertainment):
            return "Entertainment"
        elif any(term in file_name.lower() for term in nba):
            return "NBA"
        elif any(term in file_name.lower() for term in tombraider):
            return "Tomb raider"
        elif any(term in file_name.lower() for term in harry):
            return "Harry Potter"
        elif any(term in file_name.lower() for term in globalrei):
            return "Global reincarnation"
        elif any(term in file_name.lower() for term in dragonball):
            return "Dragon ball"
        elif any(term in file_name.lower() for term in comprehensive):
            return "Comprehensive"
        elif any(term in file_name.lower() for term in livebroadcast):
            return "Live Broadcast"
        elif any(term in file_name.lower() for term in shop):
            return "store"
        elif any(term in file_name.lower() for term in thriller):
            return "horror"
        elif any(term in file_name.lower() for term in Siheyuan):
            return "Siheyuan"
        elif any(term in file_name.lower() for term in ultraman):
            return "Ultraman"
        elif any(term in file_name.lower() for term in zombie):
            return "Zombie"
        elif any(term in file_name.lower() for term in survival):
            return "survival"
        elif any(term in file_name.lower() for term in hongkong):
            return "Hong Kong"
        elif any(term in file_name.lower() for term in football):
            return "football"
        elif any(term in file_name.lower() for term in tennis):
            return "tennis"
        elif any(term in file_name.lower() for term in antijp):
            return "anti-japanese"
        elif any(term in file_name.lower() for term in ygo):
            return "yugi-oh"
        elif any(term in file_name.lower() for term in bleach):
            return "bleach"
        elif any(term in file_name.lower() for term in detective):
            return "detective"
        elif any(term in file_name.lower() for term in leagueoflegends):
            return "LOL"
        elif any(term in file_name.lower() for term in demonslayer):
            return "demon slayer"
        elif any(term in file_name.lower() for term in shokugeki):
            return "shokugeki"
        elif any(term in file_name.lower() for term in rebirth):
            return "rebirth"
        elif any(term in file_name.lower() for term in system):
            return "system"
        elif any(term in file_name.lower() for term in teacher):
            return "Teacher"
        elif any(term in file_name.lower() for term in invincible):
            return "Invincible flow"
        elif any(term in file_name.lower() for term in jackie):
            return "Jackie chan"
        elif any(term in file_name.lower() for term in dynasty):
            return "China dynasty"
        elif any(term in file_name.lower() for term in tech):
            return "Tech"
        elif any(term in file_name.lower() for term in journey2west):
            return "Journey to west"
        elif any(term in file_name.lower() for term in onepunch):
            return "One-punch man"
        elif any(term in file_name.lower() for term in specialforces):
            return "Special forces"
        else:
            return "uncategorized"
