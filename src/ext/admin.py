import disnake
from disnake.ext import commands

from . import Cog


class Admin(Cog):
    @commands.slash_command(name="warn", description="Warn a user")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def warn(
        self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member, reason: str = "No reason provided"
    ) -> None:
        """Warn a user.

        Parameters
        ----------
        inter : disnake.ApplicationCommandInteraction
            The interaction
        user: disnake.Member
            The user to warn.
        reason: str
            The reason for the warning.
        """
        assert isinstance(inter.user, disnake.Member)
        if user.guild_permissions >= inter.user.guild_permissions:
            raise commands.BadArgument("You cannot warn this user.")
        try:
            await user.send(embed=disnake.Embed(title="You have been warned", description=reason, color=0xFF0000))
        except disnake.Forbidden:
            self.bot.logger.warn(f"Could not send warning message to {user}")
            raise commands.BadArgument("Could not send warning message to user")
        await self.bot.mongo.warns.add_log(user.id, reason, inter.user.id)
        await inter.response.send_message(embed=disnake.Embed(title="User warned", description=reason, color=0xFF0000))

    @commands.slash_command(name="clear", description="Clear a user's warnings")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def unwarn(
        self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member, reason: str = "No reason provided"
    ) -> None:
        """Unwarn a user.

        Parameters
        ----------
        inter : disnake.ApplicationCommandInteraction
            The interaction
        user: disnake.Member
            The user to unwarn.
        reason: str
            The reason for the unwarning.
        """
        assert isinstance(inter.user, disnake.Member)
        if user.guild_permissions >= inter.user.guild_permissions:
            raise commands.BadArgument("You cannot unwarn this user.")
        data = await self.bot.mongo.warns.get_log(user.id)
        if data is None:
            raise commands.BadArgument("User has no warnings")
        await self.bot.mongo.warns.remove_log(data.id)
        await inter.response.send_message(
            embed=disnake.Embed(title="User unwarned", description=reason, color=0xFF0000)
        )

    @commands.slash_command(name="warnings", description="Get a user's warnings")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def warnings(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member) -> None:
        """Get a user's warnings.

        Parameters
        ----------
        inter : disnake.ApplicationCommandInteraction
            The interaction
        user: disnake.Member
            The user to get the warnings of.
        """
        data = await self.bot.mongo.warns.get_log(user.id)
        if data is None:
            raise commands.BadArgument("User has no warnings")
        embed = disnake.Embed(title=f"Warnings for {user.name}", color=0xFF0000)
        for i, warn in enumerate(data.warns):
            mod = self.bot.get_user(warn.moderator) or await self.bot.fetch_user(warn.moderator)
            embed.add_field(name=f"Warning {i + 1}", value=f"Reason: {warn.reason}\nModerator: `{mod}`")
        embed.set_thumbnail(url=user.display_avatar)
        await inter.response.send_message(embed=embed)
