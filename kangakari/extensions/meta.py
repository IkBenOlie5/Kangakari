from __future__ import annotations

import inspect
import platform
import textwrap
import time
from io import BytesIO

import hikari
import lightbulb

plugin = lightbulb.Plugin("Meta")


@plugin.command
@lightbulb.command("invite", "Get the link to invite this bot.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_invite(ctx: lightbulb.context.SlashContext) -> None:
    bot_id = ctx.bot.cache.get_me().id
    await ctx.respond(
        f"Admin invite: https://discord.com/api/oauth2/authorize?client_id={bot_id}"
        "&permissions=8&scope=applications.commands%20bot\n"
        "Non admin invite: https://discord.com/api/oauth2/authorize?client_id={bot_id}"
        "&permissions=103082478656&scope=applications.commands%20bot"
    )


@plugin.command
@lightbulb.command("github", "Get the link to the GitHub of this bot.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_github(ctx: lightbulb.context.SlashContext) -> None:
    with open("./LICENSE") as f:
        license_ = f.readline().strip()
    await ctx.respond(f"This bot is licensed under the {license_}\nhttps://github.com/ikBenOlie5/kangakari")


@plugin.command
@lightbulb.option("command", "The command to get the source for")
@lightbulb.command("source", "Get the link to invite this bot.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_source(ctx: lightbulb.context.SlashContext) -> None:
    command = ctx.bot.get_slash_command(ctx.options.command)
    if command is None:
        await ctx.respond("That command doesn't exist.")
    code = textwrap.dedent((inspect.getsource(command.callback))).replace("\x60", "\u02CB")
    m = await ctx.respond(f"The source code for {command.name}.")
    b = BytesIO(code.encode())
    b.seek(0)
    await m.edit(attachment=hikari.Bytes(b, f"source_{command.name}.py"))


@plugin.command
@lightbulb.command("ping", "Get the link to invite this bot.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_ping(ctx: lightbulb.context.SlashContext) -> None:
    start = time.perf_counter()
    m = await ctx.respond("uwu")
    end = time.perf_counter()

    await m.edit(f"Gateway: {ctx.bot.heartbeat_latency *1000:,.0f} ms\nREST: {(end-start)*1000:,.0f} ms")


@plugin.command
@lightbulb.command("guild_info", "Get information about this guild.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_guild_info(ctx: lightbulb.context.SlashContext) -> None:
    guild = await ctx.bot.d.redis_cache.get_guild(ctx.guild_id)
    ms = guild.get_members()
    cs = guild.get_channels()
    guild_id = guild.id

    await ctx.respond(
        f"Created at: <t:{int(guild.created_at.timestamp())}:f>\n"
        f"Owner: `{ctx.bot.cache.get_member(guild_id, guild.owner_id).display_name}`\n"
        f"Verify level: `{str(guild.verification_level).title()}`\n"
        f"ID: `{guild_id}`\nEmojis: `{len(guild.get_emojis())}`\nRoles: `{len(guild.get_roles())}`\n\n"
        f"**Members**\nTotal: `{len(ms)}`\nHumans: `{len([m for m in ms.values() if not m.is_bot])}`\n"
        f"Bots: `{len([m for m in ms.values() if m.is_bot])}`\n\n"
        f"**Channels**\nVoice: `{len([c for c in cs.values() if c.type == hikari.ChannelType.GUILD_VOICE])}`\n"
        f"NSFW: `{len([c for c in cs.values() if c.is_nsfw])}`\n"
        f"Text: `{len([c for c in cs.values() if c.type == hikari.ChannelType.GUILD_TEXT])}`"
    )


@plugin.command
@lightbulb.option("user", "The user to get the information on.", hikari.User)
@lightbulb.command("user_info", "Get information about a user.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_user_info(ctx: lightbulb.context.SlashContext) -> None:
    user = ctx.options.user

    await ctx.respond(
        f"Created at: <t:{int(user.created_at.timestamp())}:f>\n"
        f"ID: `{user.id}`\n"
        f"Username: `{user.username}`\n"
        f"Discriminator: `#{user.discriminator}`\n"
        f"Bot? `{user.is_bot}`"
    )


@plugin.command
@lightbulb.option("user", "The user to get the avatar from.", hikari.User)
@lightbulb.command("avatar", "Get the avatar from a user.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_avatar(ctx: lightbulb.context.SlashContext) -> None:
    user = ctx.options.user
    await ctx.respond(user.avatar_url or user.default_avatar_url)


@plugin.command
@lightbulb.command("bot_info", "Get information about the bot.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_bot_info(ctx: lightbulb.context.SlashContext) -> None:
    bot_user = ctx.bot.get_me()
    await ctx.respond(
        f"Developer(s): {' | '.join(f'<@{owner_id}>' for owner_id in ctx.bot.owner_ids)}\n"
        f"Guilds: `{len(ctx.bot.cache.get_available_guilds_view())}`\n"
        f"Users: `{len(ctx.bot.cache.get_users_view())}`\n"
        f"Commands: `{len(ctx.bot.slash_commands)}`\n"
        f"Python version: `{platform.python_version()}`\n"
        f"Hikari version: `{hikari.__version__}`\n"
        f"Lightbulb version: `{lightbulb.__version__}`\n"
        f"Avatar: {bot_user.avatar_url or bot_user.default_avatar_url}"
    )

@plugin.command
@lightbulb.option("role", "The role to get the information from.", hikari.Role)
@lightbulb.command("role_info", "Get information about a role.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_role_info(ctx: lightbulb.context.SlashContext) -> None:
    role = ctx.options.role
    ms = ctx.get_guild().get_members()

    await ctx.respond(
        f"Created at: <t:{int(role.created_at.timestamp())}:f>\n"
        f"Name: `{role.name}`\n"
        f"ID: `{role.id}`\n"
        f"Administrator? `{bool(role.permissions & hikari.Permissions.ADMINISTRATOR)}`\n"
        f"Mentionable? `{role.is_mentionable}`\n"
        f"Colo(u)r: `{role.color.hex_code}`\n"
        f"Position: `{role.position}`\n"
        f"Members: `{len([m for m in  ms.values() if role.id in m.role_ids])}`"
    )





def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
