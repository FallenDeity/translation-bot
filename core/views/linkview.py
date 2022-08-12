import discord


class LinkView(discord.ui.View):
    def __init__(self, link: dict[str, list[str, str]]) -> None:
        self.link = link
        super().__init__()
        for k, v in self.link.items():
            button = discord.ui.Button(
                label=k,
                style=discord.ButtonStyle.link,
                url=v[0],
                emoji=v[1],
            )
            self.add_item(button)
