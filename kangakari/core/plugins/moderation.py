import typing

from hikari import Permissions
from hikari import errors
from lightbulb import Plugin
from lightbulb import checks
from lightbulb import commands

if typing.TYPE_CHECKING:
    from hikari import GuildTextChannel
    from hikari import Member
    from hikari import User
    from kangakari.core import Bot
    from kangakari.utils import Context


class Moderation(Plugin):
    """Commands for moderating your guild."""

    @checks.has_guild_permissions(Permissions.KICK_MEMBERS)
    @commands.command(name="kick")
    async def kick_command(self, ctx: "Context", member: "Member", *, reason: str = "No reason provided.") -> None:
        """Kick a member."""
        await member.kick(reason=reason)
        await ctx.sucess(f"Kicked `{member.display_name}`` for reason `{reason}`.")

    @checks.has_guild_permissions(Permissions.BAN_MEMBERS)
    @commands.command(name="ban")
    async def ban_command(self, ctx: "Context", member: "Member", *, reason: str = "No reason provided.") -> None:
        """Ban a member."""
        await member.ban(reason=reason)
        await ctx.sucess(f"Banned `{member.display_name}`` for reason `{reason}`.")

    @checks.has_guild_permissions(Permissions.BAN_MEMBERS)
    @commands.command(name="unban")
    async def unban_command(self, ctx: "Context", user: "User", *, reason: str = "No reason provided.") -> None:
        """Unban a user."""
        try:
            await ctx.guild.unban(user=user.id, reason=reason)
        except errors.NotFoundError:
            await ctx.warning(f"User `{user.username}` is not banned from this guild.")
            return
        await ctx.success(f"Unbanned `{user.username}`` for reason `{reason}`.")

    @checks.has_guild_permissions(Permissions.MANAGE_MESSAGES)
    @commands.command(name="clear", aliases=["purge"])
    async def clear_command(self, ctx: "Context", amount: int = 1) -> None:
        """Clear messages."""
        messages = list(await ctx.channel.fetch_history().limit(amount + 1))
        try:
            await ctx.channel.delete_messages(messages)
        except errors.BulkDeleteError:
            await ctx.error("You can only bulk delete messages that are under 14 days old.")

    @checks.has_guild_permissions(Permissions.MANAGE_MESSAGES)
    @commands.command(name="clear_channel", aliases=["clearchannel", "cc"])
    async def clear_channel_command(self, ctx: "Context", channel: typing.Optional["GuildTextChannel"]) -> None:
        """Clear an entire channel."""
        channel = channel or ctx.channel
        await ctx.guild.create_text_channel(
            name=channel.name,
            position=channel.position,
            topic=channel.topic,
            nsfw=channel.is_nsfw,
            rate_limit_per_user=channel.rate_limit_per_user,
            permission_overwrites=list(channel.permission_overwrites.values()),
            category=channel.parent_id,
            reason="Clear the entire channel.",
        )
        await channel.delete()

    @checks.has_guild_permissions(Permissions.MANAGE_NICKNAMES)
    @commands.command(name="nick")
    async def nick_command(self, ctx: "Context", member: "Member", *, nick: str = "nameless") -> None:
        """Nick a member."""
        old = member.nickname
        await member.edit(nick=nick)
        await ctx.success(f"Nicked `{old}` to `{nick}`.")


def load(bot: "Bot") -> None:
    bot.add_plugin(Moderation())


def unload(bot: "Bot") -> None:
    bot.remove_plugin("Moderation")
