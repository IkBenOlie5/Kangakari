import inspect
import textwrap
import time
import typing as t
from platform import python_version

import hikari
import lightbulb

from kangakari.core.utils import command_converter


class Meta(lightbulb.Plugin):
    """Utility commands."""

    @lightbulb.command(name="source", aliases=["src"])
    async def source_command(self, ctx: lightbulb.Context, command: command_converter) -> None:
        """Get the code of a command."""
        code = textwrap.dedent((inspect.getsource(command.callback))).replace("\x60", "\u02CB")
        await ctx.respond_embed(f"```py\n{code}```")

    @lightbulb.command(name="ping")
    async def ping_command(self, ctx: lightbulb.Context) -> None:
        """Get the bot's ping."""
        start = time.time()
        msg = await ctx.respond_embed("uwu")
        end = time.time()

        await msg.edit(
            embed=ctx.bot.embeds.build(
                ctx=ctx,
                description=f"**Gateway**: {ctx.bot.heartbeat_latency * 1000:,.0f} ms\n**REST**: {(end - start) * 1000:,.0f} ms",
            )
        )

    @lightbulb.command(name="guild_info", aliases=["guildinfo", "gi", "server_info", "serverinfo", "si"])
    async def guild_info_command(self, ctx: lightbulb.Context, guild: t.Optional[hikari.Guild] = None) -> None:
        """Get information about a guild."""
        guild = guild or ctx.guild
        guild_id = guild.id or ctx.guild_id
        ms = guild.members
        cs = guild.channels
        await ctx.respond(
            embed=ctx.bot.embeds.build(
                ctx=ctx,
                description=(
                    "\n".join(
                        [
                            f"Created at: `{guild.created_at.date().isoformat()}`",
                            f"Owner: `{ctx.bot.cache.get_member(guild_id, guild.owner_id).display_name}`",
                            f"Verify level: `{str(guild.verification_level).title()}`",
                            f"ID: `{guild_id}`",
                            f"Emojis: `{len(guild.emojis)}`",
                            f"Roles: `{len(guild.roles)}`",
                        ]
                    )
                ),
                fields=[
                    (
                        "Members",
                        "\n".join(
                            [
                                f"Total: `{len(ms)}`",
                                f":adult:Humans: `{len([ms[m_id] for m_id in ms if not ms[m_id].is_bot])}`",
                                f":robot:Bots: `{len([ms[m_id] for m_id in ms if ms[m_id].is_bot])}`",
                            ]
                        ),
                        True,
                    ),
                    (
                        "Channels",
                        "\n".join(
                            [
                                f":sound:Voice: `{len([cs[c_id] for c_id in cs if cs[c_id].type == hikari.ChannelType.GUILD_VOICE])}`",
                                f":underage:NSFW: `{len([cs[c_id] for c_id in cs if cs[c_id].is_nsfw])}`",
                                f":speech_balloon:Text: `{len([cs[c_id] for c_id in cs if cs[c_id].type == hikari.ChannelType.GUILD_TEXT])}`",
                            ]
                        ),
                        True,
                    ),
                ],
                thumbnail=guild.icon_url,
            )
        )

    @lightbulb.command(name="user_info", aliases=["userinfo", "ui", "member_info", "memberinfo", "mi"])
    async def user_info_command(self, ctx: lightbulb.Context, user: t.Optional[hikari.User] = None) -> None:
        """Get information about a user."""
        user = user or ctx.author
        await ctx.respond(
            embed=ctx.bot.embeds.build(
                ctx=ctx,
                description="\n".join(
                    [
                        f"Created at: `{user.created_at.date().isoformat()}`",
                        f"ID: `{user.id}`",
                        f"Username: `{user.username}`",
                        f"Discriminator: `{user.discriminator}`",
                        f":robot:Bot? `{user.is_bot}`",
                    ]
                ),
                thumbnail=user.avatar_url or user.default_avatar_url,
            )
        )

    @lightbulb.command(name="avatar", aliases=["av", "profile", "pf"])
    async def avatar_command(self, ctx: lightbulb.Context, user: t.Optional[hikari.User] = None) -> None:
        """Get the avatar of a user."""
        user = user or ctx.author
        await ctx.respond(embed=ctx.bot.embeds.build(ctx=ctx, image=user.avatar_url or user.default_avatar_url))

    @lightbulb.command(name="bot_info", aliases=["botinfo", "bi", "about", "abt"])
    async def bot_info_command(self, ctx: lightbulb.Context) -> None:
        """Get information about the bot."""
        await ctx.respond(
            embed=ctx.bot.embeds.build(
                ctx=ctx,
                description="\n".join(
                    [
                        f"Developer(s): {' | '.join(f'<@{owner_id}>' for owner_id in ctx.bot.owner_ids)}",
                        f"Guilds: `{len(ctx.bot.cache.get_available_guilds_view())}`",
                        f":adult:Users: `{len(ctx.bot.cache.get_users_view())}`",
                        f"Commands: `{len(ctx.bot.commands)}`",
                        f"Database calls: `{ctx.bot.db.calls}`",
                        f"Python version: `{python_version()}`",
                        f"Hikari version: `{hikari.__version__}`",
                        f"Lightbulb version: `{lightbulb.__version__}`",
                    ]
                ),
                thumbnail=ctx.bot.me.avatar_url or ctx.bot.me.default_avatar_url,
            )
        )

    @lightbulb.command(name="role_info", aliases=["roleinfo", "ri"])
    async def role_info_command(self, ctx: lightbulb.Context, role: t.Optional[hikari.Role] = None) -> None:
        """Get information about a role."""
        role = role or ctx.member.top_role
        await ctx.respond(
            embed=ctx.bot.embeds.build(
                ctx=ctx,
                description="\n".join(
                    [
                        f"Created at: `{role.created_at.date().isoformat()}`",
                        f"Name: `{role.name}`",
                        f"ID: `{role.id}`",
                        f":hammer:Administrator? `{bool(role.permissions & hikari.Permissions.ADMINISTRATOR)}`",
                        f":cyclone:Mentionable? `{role.is_mentionable}`",
                        f"Hoisted? `{role.is_hoisted}`",
                        f"Colo(u)r: `{role.color.hex_code}`",
                        f"Position: `{role.position}`",
                    ]
                ),
                thumbnail=ctx.guild.icon_url,
            )
        )


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Meta())


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Meta")