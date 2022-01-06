from __future__ import annotations

import datetime

import hikari
import lightbulb

from kangakari.utils import helpers

plugin = lightbulb.Plugin("Mod")


@plugin.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.KICK_MEMBERS))
@lightbulb.option("member", "The member to kick.", hikari.Member)
@lightbulb.option("reason", "The reason to kick.", required=False)
@lightbulb.command("kick", "Kick a member.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_kick(ctx: lightbulb.context.SlashContext) -> None:
    member = ctx.options.member
    reason = ctx.options.reason
    await member.kick(reason=reason)
    await ctx.respond(f"Kicked `{member.display_name}` for reason `{reason}`.")


@plugin.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.BAN_MEMBERS))
@lightbulb.option("user", "The user to ban.", hikari.User)
@lightbulb.option("reason", "The reason to ban.", required=False)
@lightbulb.option("delete_message_days", "For how many days do the messages have to be deleted (0-7).", int, default=0)
@lightbulb.command("ban", "Ban a user.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_ban(ctx: lightbulb.context.SlashContext) -> None:
    delete_message_days = ctx.options.delete_message_days
    if not 0 <= delete_message_days <= 7:
        await ctx.respond("delete_message_days must be between 0 and 7.")
        return
    user = ctx.options.user
    reason = ctx.options.reason
    await ctx.get_guild().ban(user, delete_message_days=delete_message_days, reason=reason)
    await ctx.respond(
        f"Banned `{user.username}` for reason `{reason}` "
        f"and deleted their messages for `{delete_message_days}` days."
    )


@plugin.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.BAN_MEMBERS))
@lightbulb.option("user", "The user to unban.", hikari.User)
@lightbulb.option("reason", "The reason to unban.", required=False)
@lightbulb.command("unban", "Unban a member.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_unban(ctx: lightbulb.context.SlashContext) -> None:
    user = ctx.options.user
    reason = ctx.options.reason
    try:
        await ctx.get_guild().unban(user, reason=reason)
    except hikari.NotFoundError:
        await ctx.respond("That user is not banned from this guild.")
        return
    await ctx.respond(f"Unbanned `{user.username}` for reason `{reason}`.")


@plugin.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES))
@lightbulb.option("amount", "The amount of messages to clear.", int)
@lightbulb.command("clear", "Clear messages.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_clear(ctx: lightbulb.context.SlashContext) -> None:
    channel = ctx.get_channel()
    messages = list(await channel.fetch_history().limit(ctx.options.amount + 1))
    try:
        await channel.delete_messages(messages)
    except hikari.BulkDeleteError:
        await ctx.respond("You can only bulk delete messages that are under 14 days old.")


@plugin.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES))
@lightbulb.option("channel", "The channel to clear.", hikari.TextableGuildChannel)
@lightbulb.command("clear_channel", "Clear a channel.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_clear(ctx: lightbulb.context.SlashContext) -> None:
    channel = await ctx.bot.d.redis_cache.get_guild_channel(ctx.options.channel.id)
    await ctx.get_guild().create_text_channel(
        name=channel.name,
        position=channel.position,
        topic=channel.topic,
        nsfw=channel.is_nsfw,
        rate_limit_per_user=channel.rate_limit_per_user,
        permission_overwrites=list(channel.permission_overwrites.values()),
        category=channel.parent_id,
        reason="Clear the channel.",
    )
    await channel.delete()


@plugin.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_NICKNAMES))
@lightbulb.option("nick", "The nick to change the member to.")
@lightbulb.option("member", "The member to change the nick of.", hikari.Member)
@lightbulb.command("nick", "Nick a member.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_nick(ctx: lightbulb.context.SlashContext) -> None:
    member = ctx.options.member
    nick = ctx.options.nick
    old = member.nickname
    await member.edit(nick=nick)
    await ctx.respond(f"Nicked `{old}` to `{nick}`.")


@plugin.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_NICKNAMES))
@lightbulb.option("timedelta", "How long to time them out.")
@lightbulb.option("member", "The member to timeout.", hikari.Member)
@lightbulb.command("timeout", "Time a member out.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_timeout(ctx: lightbulb.context.SlashContext) -> None:
    timedelta = helpers.str_to_timedelta(ctx.options.timedelta)
    if timedelta is None:
        await ctx.respond("Couldn't convert timedelta.")
        return
    member = ctx.options.member
    communication_disabled_until = datetime.datetime.utcnow() + timedelta
    await member.edit(communication_disabled_until=communication_disabled_until)
    await ctx.respond(f"Timed out `{member.display_name}` until <t:{int(communication_disabled_until.timestamp())}:f>.")


@plugin.command
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_NICKNAMES))
@lightbulb.option("member", "The member to timeout.", hikari.Member)
@lightbulb.command("remove_timeout", "timeout a member.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_timeout(ctx: lightbulb.context.SlashContext) -> None:
    member = ctx.options.member
    await member.edit(communication_disabled_until=None)
    await ctx.respond(f"Removed timeout from `{member.display_name}`.")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
