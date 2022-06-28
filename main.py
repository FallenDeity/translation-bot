import asyncio
import os
import docx
from discord import ui
from discord.ext import menus
from filestack import Client
import zipfile
import requests
import discord
import chardet
from bs4 import BeautifulSoup
import aiofiles
from itertools import starmap, chain
from deep_translator import GoogleTranslator
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from discord.ext import commands, tasks

bot = commands.Bot(command_prefix=commands.when_mentioned_or('.t'), intents=discord.Intents.all())
rate = {}
track = []
crawler = {}
choices = {'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'arabic': 'ar', 'armenian': 'hy', 'azerbaijani': 'az', 'basque': 'eu', 'belarusian': 'be', 'bengali': 'bn', 'bosnian': 'bs', 'bulgarian': 'bg', 'catalan': 'ca', 'cebuano': 'ceb', 'chichewa': 'ny', 'chinese (simplified)': 'zh-CN', 'chinese (traditional)': 'zh-TW', 'corsican': 'co', 'croatian': 'hr', 'czech': 'cs', 'danish': 'da', 'dutch': 'nl', 'english': 'en', 'esperanto': 'eo', 'estonian': 'et', 'filipino': 'tl', 'finnish': 'fi', 'french': 'fr', 'frisian': 'fy', 'galician': 'gl', 'georgian': 'ka', 'german': 'de', 'greek': 'el', 'gujarati': 'gu', 'haitian creole': 'ht', 'hausa': 'ha', 'hawaiian': 'haw', 'hebrew': 'iw', 'hindi': 'hi', 'hmong': 'hmn', 'hungarian': 'hu', 'icelandic': 'is', 'igbo': 'ig', 'indonesian': 'id', 'irish': 'ga', 'italian': 'it', 'japanese': 'ja', 'javanese': 'jw', 'kannada': 'kn', 'kazakh': 'kk', 'khmer': 'km', 'kinyarwanda': 'rw', 'korean': 'ko', 'kurdish': 'ku', 'kyrgyz': 'ky', 'lao': 'lo', 'latin': 'la', 'latvian': 'lv', 'lithuanian': 'lt', 'luxembourgish': 'lb', 'macedonian': 'mk', 'malagasy': 'mg', 'malay': 'ms', 'malayalam': 'ml', 'maltese': 'mt', 'maori': 'mi', 'marathi': 'mr', 'mongolian': 'mn', 'myanmar': 'my', 'nepali': 'ne', 'norwegian': 'no', 'odia': 'or', 'pashto': 'ps', 'persian': 'fa', 'polish': 'pl', 'portuguese': 'pt', 'punjabi': 'pa', 'romanian': 'ro', 'russian': 'ru', 'samoan': 'sm', 'scots gaelic': 'gd', 'serbian': 'sr', 'sesotho': 'st', 'shona': 'sn', 'sindhi': 'sd', 'sinhala': 'si', 'slovak': 'sk', 'slovenian': 'sl', 'somali': 'so', 'spanish': 'es', 'sundanese': 'su', 'swahili': 'sw', 'swedish': 'sv', 'tajik': 'tg', 'tamil': 'ta', 'tatar': 'tt', 'telugu': 'te', 'thai': 'th', 'turkish': 'tr', 'turkmen': 'tk', 'ukrainian': 'uk', 'urdu': 'ur', 'uyghur': 'ug', 'uzbek': 'uz', 'vietnamese': 'vi', 'welsh': 'cy', 'xhosa': 'xh', 'yiddish': 'yi', 'yoruba': 'yo', 'zulu': 'zu'}


from itertools import chain, starmap

import discord
from discord import ui
from discord.ext import commands, menus


class MyMenuPages(ui.View, menus.MenuPages):
    def __init__(self, source, *, delete_message_after=False):
        super().__init__(timeout=60)
        self._source = source
        self.current_page = 0
        self.ctx = None
        self.message = None
        self.delete_message_after = delete_message_after

    async def start(self, ctx, *, channel=None, wait=False):
        await self._source._prepare_once()
        self.ctx = ctx
        self.message = await self.send_initial_message(ctx, ctx.channel)

    async def _get_kwargs_from_page(self, page):
        value = await super()._get_kwargs_from_page(page)
        if "view" not in value:
            value.update({"view": self})
        return value

    async def interaction_check(self, interaction):
        return interaction.user == self.ctx.author

    @ui.button(
        emoji="<:DoubleArrowLeft:989134953142956152>",
        style=discord.ButtonStyle.blurple,
    )
    async def first_page(self, button, interaction):
        await button.response.defer()
        return await self.show_page(0)

    @ui.button(
        emoji="<:ArrowLeft:989134685068202024>", style=discord.ButtonStyle.blurple
    )
    async def before_page(self, button, interaction):
        await button.response.defer()
        return await self.show_checked_page(self.current_page - 1)

    @ui.button(emoji="<:dustbin:989150297333043220>", style=discord.ButtonStyle.blurple)
    async def stop_page(self, button, interaction):
        self.stop()
        if self.delete_message_after:
            return await self.message.delete(delay=0)

    @ui.button(
        emoji="<:rightArrow:989136803284004874>", style=discord.ButtonStyle.blurple
    )
    async def next_page(self, button, interaction):
        await button.response.defer()
        return await self.show_checked_page(self.current_page + 1)

    @ui.button(
        emoji="<:DoubleArrowRight:989134892384256011>",
        style=discord.ButtonStyle.blurple,
    )
    async def last_page(self, button, interaction):
        await button.response.defer()
        return await self.show_page(self._source.get_max_pages() - 1)


class HelpPageSource(menus.ListPageSource):
    def __init__(self, data, helpcommand, mode):
        super().__init__(data, per_page=3)
        self.helpcommand = helpcommand
        self.mode = mode

    def format_command_help(self, no, command):
        signature = (
            str(self.helpcommand.get_command_signature(command))
            .lower()
            .replace("=none", "")
        )
        signature += (30 - len(signature)) * " "
        docs = command.short_doc or "Command is not documented."
        return f"**`{no})`  {command.qualified_name.title()}**```\n{signature}             ```*{docs}*".replace(
            "[", "<"
        ).replace(
            "]", ">"
        )

    async def format_page(self, menu, entries):
        page = menu.current_page
        max_page = self.get_max_pages()
        starting_number = page * self.per_page + 1
        iterator = starmap(
            self.format_command_help, enumerate(entries, start=starting_number)
        )
        page_content = "\n\n".join(iterator)
        embed = discord.Embed(
            title=f"{self.mode} Command",
            description=page_content,
            color=discord.Color.random(),
        )
        author = menu.ctx.author
        embed.set_thumbnail(url=menu.ctx.bot.user.display_avatar)
        embed.set_footer(
            text=f"{page + 1}/{max_page} | Requested by {author.name}",
            icon_url=author.display_avatar,
        )  # author.avatar in 2.0
        return embed


class MyHelp(commands.MinimalHelpCommand):
    async def send_bot_help(self, mapping):
        all_commands = list(chain.from_iterable(mapping.values()))
        formatter = HelpPageSource(all_commands, self, "Help")
        menu = MyMenuPages(formatter, delete_message_after=True)
        await menu.start(self.context)

    async def send_group_help(self, group):
        subcommands = group.commands
        if len(subcommands) == 0:
            return await self.send_command_help(group)
        filtered = await self.filter_commands(subcommands, sort=True)
        filtered.insert(0, group)
        formatter = HelpPageSource(filtered, self, f"{group.qualified_name}")
        menu = MyMenuPages(formatter, delete_message_after=True)
        await menu.start(self.context)

    async def send_command_help(self, command):
        embed = discord.Embed(
            color=discord.Color.random(),
            title=f"{command.qualified_name.title()} Command",
        )
        if command.description:
            embed.description = f"{command.description}\n\n{command.help}"
        else:
            embed.description = command.help or "No help found..."
        embed.add_field(
            name="Usage",
            value=f"```{self.get_command_signature(command).lower().replace('=none', '')}```",
        )
        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(command.aliases))
        embed.set_thumbnail(url=self.context.bot.user.display_avatar)
        embed.set_footer(text=f"Requested by {self.context.author.name}")
        await self.context.send(embed=embed)
        
        
bot.help_command = MyHelp()


def translates(liz, order, author, lang):
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(download_image, [url], num, lang) for num, url in enumerate(liz)]
        for future in concurrent.futures.as_completed(futures):
            order[future.result()[0]] = future.result()[1]
            rate[author] = f"{len(order)}/{len(liz)}"
        return order


def download_image(img_url, num, lang):
    translated = GoogleTranslator(source='auto', target=lang).translate_batch(img_url)
    return num, translated


@tasks.loop(seconds=120)
async def census():
  await bot.wait_until_ready()
  await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.users)} novel enthusiasts. Prefix: .t"))
  for i, j in rate.items():
        if j.split('/')[0] == '0' and i in track:
            member = bot.get_member(i) or await bot.get_member(i) 
            await member.send(f"sorry your novel is unable to be translated.")
            track.remove(i)
            del rate[i]


@bot.event 
async def on_ready():
    print(f'Running as {bot.user}')
    census.start()


@bot.command(help='Gives progress of novel translation', aliases=['now', 'n', 'p'])
async def progress(ctx):
    if ctx.author.id not in rate: return await ctx.send("**You have no novel deposited for translation currently.**")
    await ctx.send(f"**🚄`{rate[ctx.author.id]}`**")


def ask(link):
  resp = requests.get(link)
  return resp


@bot.command(help='Send along with ur novel txt or doc or link to auto translate. Currently supports only https://temp.sh', aliases=['t'])
async def translate(ctx, language='english', link=None):
    string = ["{0: ^17}".format(f"{k} --> {v}") for k, v in choices.items()]
    string = '\n'.join([''.join(string[i:i+3]) for i in range(0, len(string), 3)])
    await ctx.typing()
    total = []
    for k, v in choices.items():
        total.append(k)
        total.append(v)
    if language not in total: return await ctx.reply(f"**We have the following languages in our db.**\n```{string}```")
    if ctx.author.id in rate: return await ctx.send('**⛔You cant translate two novels at a time.**')
    if not ctx.message.attachments and not link: return await ctx.send('**⛔You must add a novel/link to translate**')
    if link:
        resp = await bot.loop.run_in_executor(None, ask, 
    link)
        try: 
          file_type = ''.join([i for i in resp.headers['Content-Disposition'].split('.')[-1] if i.isalnum()])
        except: 
          return await ctx.send("Currently this link is not supported.please try with https://temp.sh")
        name = link.split('/')[-1].replace('.txt', '').replace('.docx', '')
    else:
        name = ctx.message.attachments[0].filename.replace('.txt', '').replace('.docx', '')
        resp = await bot.loop.run_in_executor(None, ask, ctx.message.attachments[0].url)
        file_type = resp.headers['content-type'].split('/')[-1]
    if 'plain' in file_type.lower() or 'txt' in file_type.lower(): file_type = 'txt'
    elif 'document' in file_type.lower() or 'docx' in file_type.lower(): file_type = 'docx'
    else: return await ctx.send('Only .docx and .txt supported')
    async with aiofiles.open(f'{ctx.author.id}.{file_type}', 'wb') as f: await f.write(resp.content)
    if 'docx' in file_type:
        await ctx.reply('**Docx file detected please wait while we finish converting.**')
        await ctx.typing()
        doc = docx.Document(f'{ctx.author.id}.{file_type}')
        string = '\n'.join([para.text for para in doc.paragraphs])
        async with aiofiles.open(f'{ctx.author.id}.txt', 'w', encoding='utf-8') as f: await f.write(string)
        os.remove(f'{ctx.author.id}.docx')
    try:
        async with aiofiles.open(f'{ctx.author.id}.txt', 'r', encoding='utf-8') as f: novel = await f.read()
    except:
        try:
            async with aiofiles.open(f'{ctx.author.id}.txt', 'r', encoding='cp936') as f: novel = await f.read()
        except:
            try:
                async with aiofiles.open(f'{ctx.author.id}.txt', 'r', encoding='utf-16') as f: novel = await f.read()
            except:
                try:
                    async with aiofiles.open(f'{ctx.author.id}.txt', 'r', encoding='cp949') as f: novel = await f.read()
                except:
                    try:
                        await ctx.send('**encoding not in db trying to auto detect please be patient**')
                        async with aiofiles.open(f'{ctx.author.id}.txt', 'rb') as f: novel = await f.read()
                        async with aiofiles.open(f'{ctx.author.id}.txt', 'r', encoding=chardet.detect(novel[:250])['encoding']) as f: novel= await f.read()
                    except Exception as e:
                        print(e)
                        return await ctx.reply("**⛔Currently we are only translating korean and chinese.**")        
    await ctx.reply(f'**✅Translation started. Translating to {language}.**')
    track.append(ctx.author.id)
    os.remove(f'{ctx.author.id}.txt')
    liz = [novel[i:i+1800] for i in range(0, len(novel), 1800)]
    order = {}
    rate[ctx.author.id] = f"0/{len(liz)}"
    translated = await bot.loop.run_in_executor(None, translates, liz, order, ctx.author.id, language)
    comp = {k: v for k, v in sorted(translated.items(), key=lambda item: item[0])}
    full = [i[0] for i in list(comp.values()) if i[0] is not None]
    async with aiofiles.open(f'{ctx.author.id}.txt', 'w', encoding='utf-8') as f: await f.write(" ".join(full))
    if os.path.getsize(f"{ctx.author.id}.txt") > 8*10**6:
        c = Client("AXiAEgFvETpKeqBHufPBXz")
        try:
            with zipfile.ZipFile(f'{ctx.author.id}.zip', 'w') as jungle_zip: jungle_zip.write(f'{ctx.author.id}.txt', compress_type=zipfile.ZIP_DEFLATED)
            filelnk = c.upload(filepath = f"{ctx.author.id}.zip")
            await ctx.reply(f"**{name}: here is your novel {filelnk.url}**")
        except:
            await ctx.reply("**Sorry your file was too big please split it and try again.**")
        os.remove(f"{ctx.author.id}.zip")
    else:
        file = discord.File(f"{ctx.author.id}.txt", f"{name}.txt")
        await ctx.reply("**🎉Here is your translated novel**", file=file)
    os.remove(f"{ctx.author.id}.txt")
    del rate[ctx.author.id]
    track.remove(ctx.author.id)
    
    
@bot.command(help='Clears any stagnant novels which were deposited for translation.')
async def clear(ctx):
    if ctx.author.id in rate:
        if rate[ctx.author.id].split('/')[0] == '0':
            del rate[çtx.author.id]
        else:
            return await ctx.reply(f"**There is a novel translation going on currently.**")
    if ctx.author.id in track:
        track.remove(ctx.author.id)
    files = os.listdir()
    for i in files:
        if str(ctx.author.id) in str(i) and 'crawl' not in i:
            os.remove(i)
    await ctx.reply("**Cleared all records.**")
    
 
def easy(nums, links):
    data = requests.get(links)
    soup = BeautifulSoup(data.content, 'lxml')
    text = soup.find_all(text=True)
    full = ''.join([i for i in text if i not in blacklist])
    return nums, full
    
    
def direct():
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(easy, i, j) for i, j in enumerate(urls)]
        for future in concurrent.futures.as_completed(futures):
            novel[future.result()[0]] = future.result()[1]
            crawler[name] = f'{len(novel)}/{len(urls)}'
            
@bot.command(help='Gives progress of novel crawling', aliases=['cp'])
async def crawled(ctx):
    if ctx.author.id not in crawler: return await ctx.send("**You have no novel deposited for crawling currently.**")
    await ctx.send(f"**🚄`{crawler[ctx.author.id]}`**")
    
    
@bot.command(help='Crawls other sites for novels. Currently available trxs, tongrenquan, ffxs.')
async def crawl(ctx, link=None):
    if ctx.author.id in crawler:
        return await ctx.reply("**You cannot crawl two novels at the same time.**")
    allowed = ['trxs', 'tongrenquan', 'ffxs']
    if link is None:
        return await ctx.reply(f"**Enter a link for crawling.**")
    num = 0
    for i in allowed:
        if i not in link:
            num += 1
    if num == 3:
        return await ctx.reply(f"**We currently crawl only from {', '.join(allowed)}**")
    res = await bot.loop.run_in_executor(None, ask, link)
    novel = {}
    soup = BeautifulSoup(res.text, 'html.parser')
    name = str(link.split('/')[-1].replace('.html', ''))
    print(name)
    frontend_part = link.replace(f'/{name}', '').split('/')[-1]
    frontend = link.replace(f'/{name}', '').replace(f'/{frontend_part}', '')
    print(frontend)
    urls = [f'{frontend}{j}' for j in [str(i.get('href')) for i in soup.find_all('a')] if name in j and '.html' in j and 'txt' not in j]
    print(len(urls))
    maxs = len(urls)
    name = ctx.author.id
    crawler[ctx.author.id] = f'0/{len(urls)}'
    await ctx.reply(f"**Crawl started.**")
    await bot.loop.run_in_executor(None, direct)
    parsed = {k:v for k, v in sorted(novel.items(), key=lambda item: item[0])}
    full = [i for i in list(parsed.values())]
    async with aiofiles.open(f'{ctx.author.id}_crawl.txt', 'w', encoding='utf-8') as f: await f.write("\n".join(full))
    if os.path.getsize(f"{ctx.author.id}_crawl.txt") > 8*10**6:
        c = Client("AXiAEgFvETpKeqBHufPBXz")
        try:
            with zipfile.ZipFile(f'{ctx.author.id}_crawl.zip', 'w') as jungle_zip: jungle_zip.write(f'{ctx.author.id}_crawl.txt', compress_type=zipfile.ZIP_DEFLATED)
            filelnk = c.upload(filepath = f"{ctx.author.id}.zip")
            await ctx.reply(f"**{ctx.author.mention}: here is your novel {filelnk.url}**")
        except:
            await ctx.reply("**Sorry the file is too big to send.**")
        os.remove(f"{ctx.author.id}_crawl.zip")
    else:
        file = discord.File(f"{ctx.author.id}_crawl.txt", f"{link}.txt")
        await ctx.reply("**🎉Here is your translated novel**", file=file)
    os.remove(f"{ctx.author.id}_crawl.txt")
    del crawler[ctx.author.id]

    

async def main():
    async with bot:
        await bot.start(os.getenv('TOKEN'))

asyncio.run(main())
