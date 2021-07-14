import typing as t

import hikari
import lightbulb


class Moderation(lightbulb.Plugin):
    @lightbulb.has_guild_permissions(hikari.Permissions.KICK_MEMBERS)
    @lightbulb.command(name="kick")
    async def kick_command(
        self, ctx: lightbulb.Context, member: hikari.Member, *, reason: str = "No reason provided."
    ) -> None:
        await member.kick(reason=reason)
        await ctx.respond_embed(f"Kicked `{member.display_name}`` for reason `{reason}`.")

    @lightbulb.has_guild_permissions(hikari.Permissions.BAN_MEMBERS)
    @lightbulb.command(name="ban")
    async def ban_command(
        self, ctx: lightbulb.Context, member: hikari.Member, *, reason: str = "No reason provided."
    ) -> None:
        await member.ban(reason=reason)
        await ctx.respond_embed(f"Banned `{member.display_name}`` for reason `{reason}`.")

    @lightbulb.has_guild_permissions(hikari.Permissions.BAN_MEMBERS)
    @lightbulb.command(name="unban")
    async def unban_command(
        self, ctx: lightbulb.Context, user: hikari.User, *, reason: str = "No reason provided."
    ) -> None:
        try:
            await ctx.guild.unban(user=user, reason=reason)
        except hikari.errors.NotFoundError:
            return await ctx.respond_embed(f"User `{user.username}` is not banned from this guild.")
        await ctx.respond_embed(f"Unbanned `{user.username}`` for reason `{reason}`.")

    @lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES)
    @lightbulb.command(name="clear", aliases=["purge"])
    async def clear_command(self, ctx: lightbulb.Context, amount: int = 1) -> None:
        messages = list(await ctx.channel.fetch_history().limit(amount + 1))
        await ctx.channel.delete_messages(messages)

    @lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES)
    @lightbulb.command(name="clear_channel", aliases=["cc"])
    async def clear_channel_command(
        self, ctx: lightbulb.Context, channel: t.Optional[hikari.GuildTextChannel]
    ) -> None:
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

    @lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_NICKNAMES)
    @lightbulb.command(name="nick")
    async def nick_command(self, ctx: lightbulb.Context, member: hikari.Member, *, nick: str = "nameless") -> None:
        old = member.nickname
        await member.edit(nick=nick)
        await ctx.respond_embed(f"Nicked `{old}` to `{nick}`.")


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Moderation())


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Moderation")
