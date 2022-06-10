import asyncio
import os
import docx
from discord import ui
from discord.ext import menus
import requests
import discord
import aiofiles
from itertools import starmap, chain
from deep_translator import GoogleTranslator
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from discord.ext import commands, tasks

bot = commands.Bot(command_prefix=commands.when_mentioned_or('.t'), intents=discord.Intents.all())
rate = {}


class MyMenuPages(ui.View, menus.MenuPages):
    def __init__(self, source, *, delete_message_after=False):
        super().__init__(timeout=60)
        self._source = source
        self.current_page = 0
        self.ctx = None
        self.message = None
        self.delete_message_after = delete_message_after

    async def start(self, ctx, *, channel=None, wait=False):
        # We wont be using wait/channel, you can implement them yourself. This is to match the MenuPages signature.
        await self._source._prepare_once()
        self.ctx = ctx
        self.message = await self.send_initial_message(ctx, ctx.channel)

    async def _get_kwargs_from_page(self, page):
        """This method calls ListPageSource.format_page class"""
        value = await super()._get_kwargs_from_page(page)
        if 'view' not in value:
            value.update({'view': self})
        return value

    async def interaction_check(self, interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        return interaction.user == self.ctx.author

    @ui.button(emoji='<:before_fast_check:754948796139569224>', style=discord.ButtonStyle.blurple)
    async def first_page(self, button, interaction):
        await self.show_page(0)

    @ui.button(emoji='<:before_check:754948796487565332>', style=discord.ButtonStyle.blurple)
    async def before_page(self, button, interaction):
        await self.show_checked_page(self.current_page - 1)

    @ui.button(emoji='<:stop_check:754948796365930517>', style=discord.ButtonStyle.blurple)
    async def stop_page(self, button, interaction):
        self.stop()
        if self.delete_message_after:
            await self.message.delete(delay=0)

    @ui.button(emoji='<:next_check:754948796361736213>', style=discord.ButtonStyle.blurple)
    async def next_page(self, button, interaction):
        await self.show_checked_page(self.current_page + 1)

    @ui.button(emoji='<:next_fast_check:754948796391227442>', style=discord.ButtonStyle.blurple)
    async def last_page(self, button, interaction):
        await self.show_page(self._source.get_max_pages() - 1)


class HelpPageSource(menus.ListPageSource):
    def __init__(self, data, helpcommand):
        super().__init__(data, per_page=6)
        self.helpcommand = helpcommand

    def format_command_help(self, no, command):
        signature = self.helpcommand.get_command_signature(command)
        docs = self.helpcommand.get_command_brief(command)
        return f"**{no})** **{signature}**\n*{docs}*"

    async def format_page(self, menu, entries):
        page = menu.current_page
        max_page = self.get_max_pages()
        starting_number = page * self.per_page + 1
        iterator = starmap(self.format_command_help, enumerate(entries, start=starting_number))
        page_content = "\n\n".join(iterator)
        embed = discord.Embed(
            title=f"Help Command [{page + 1}/{max_page}]",
            description=page_content,
            color=0xffcccb
        )
        author = menu.ctx.author
        embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)  # author.avatar in 2.0
        return embed


class MyHelp(commands.MinimalHelpCommand):

    def get_command_brief(self, command):
        return command.short_doc or "Command is not documented."

    async def send_bot_help(self, mapping):
        all_commands = list(chain.from_iterable(mapping.values()))
        formatter = HelpPageSource(all_commands, self)
        menu = MyMenuPages(formatter, delete_message_after=True)
        await menu.start(self.context)

    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command), color=discord.Colour.random())
        embed.add_field(name="Help", value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)


bot.help_command = MyHelp()


def translates(liz, order, author):
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(download_image, [url], num) for num, url in enumerate(liz)]
        for future in concurrent.futures.as_completed(futures):
            order[future.result()[0]] = future.result()[1]
            rate[author] = f"{len(order)}/{len(liz)}"
        return order


def download_image(img_url, num):
    translated = GoogleTranslator(source='auto', target='english').translate_batch(img_url)
    return num, translated


@tasks.loop(seconds=120)
async def census():
  await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.users)} novel enthusiasts. Prefix: .t"))


@bot.event 
async def on_ready():
    print(f'Running as {bot.user}')
    census.start()


@bot.command(help='Gives progress of novel translation', aliases=['now', 'n', 'p'])
async def progress(ctx):
    if ctx.author.id not in rate: return await ctx.send("**You have no novel deposited for translation currently.**")
    await ctx.send(f"**🚄{rate[ctx.author.id]}**")


def ask(link):
  resp = requests.get(link)
  return resp


@bot.command(help='Send along with ur novel txt or doc or link to auto translate. Currently supports only https://temp.sh', aliases=['t'])
async def translate(ctx, link=None):
    await ctx.typing()
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
                except Exception as e:
                    print(e)
                    return await ctx.reply("**⛔Currently we are only translating korean and chinese.**")        
    await ctx.reply('**✅Translation started**')
    os.remove(f'{ctx.author.id}.txt')
    liz = [novel[i:i+1800] for i in range(0, len(novel), 1800)]
    order = {}
    rate[ctx.author.id] = f"0/{len(liz)}"
    translated = await bot.loop.run_in_executor(None, translates, liz, order, ctx.author.id)
    comp = {k: v for k, v in sorted(translated.items(), key=lambda item: item[0])}
    full = [i[0] for i in list(comp.values())]
    async with aiofiles.open(f'{ctx.author.id}.txt', 'w', encoding='utf-8') as f: await f.write(" ".join(full))
    file = discord.File(f"{ctx.author.id}.txt", f"{name}.txt")
    await ctx.reply("**🎉Here is your translated novel**", file=file)
    os.remove(f"{ctx.author.id}.txt")
    del rate[ctx.author.id]
    

async def main():
    async with bot:
        await bot.start(os.getenv('TOKEN'))

asyncio.run(main())
