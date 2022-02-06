from __future__ import annotations

import hikari
import lightbulb

plugin = lightbulb.Plugin("Mod")


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
async def cmd_clear_channel(ctx: lightbulb.context.SlashContext) -> None:
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


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
