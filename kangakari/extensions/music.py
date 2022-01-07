from __future__ import annotations

import logging

import hikari
import lavasnek_rs
import lightbulb

from kangakari import Config

plugin = lightbulb.Plugin("Music")

log = logging.getLogger(__name__)


class EventHandler:
    async def track_start(self, _: lavasnek_rs.Lavalink, event: lavasnek_rs.TrackStart) -> None:
        log.info("Track started on guild: %s", event.guild_id)

    async def track_finish(self, _: lavasnek_rs.Lavalink, event: lavasnek_rs.TrackFinish) -> None:
        log.info("Track finished on guild: %s", event.guild_id)

    async def track_exception(self, lavalink: lavasnek_rs.Lavalink, event: lavasnek_rs.TrackException) -> None:
        log.warning("Track exception event happened on guild: %d", event.guild_id)

        skip = await lavalink.skip(event.guild_id)
        node = await lavalink.get_guild_node(event.guild_id)

        if not node:
            return

        if skip and not node.queue and not node.now_playing:
            await lavalink.stop(event.guild_id)


async def _join(ctx: lightbulb.Context) -> hikari.Snowflake | None:
    assert ctx.guild_id is not None

    states = plugin.bot.cache.get_voice_states_view_for_guild(ctx.guild_id)
    voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == ctx.author.id)]

    if not voice_state:
        await ctx.respond("Connect to a voice channel first.")
        return None

    channel_id = voice_state[0].channel_id

    await plugin.bot.update_voice_state(ctx.guild_id, channel_id, self_deaf=True)
    connection_info = await plugin.bot.d.lavalink.wait_for_full_connection_info_insert(ctx.guild_id)

    await plugin.bot.d.lavalink.create_session(connection_info)

    return channel_id


@plugin.listener(hikari.ShardReadyEvent)
async def on_shard_ready(event: hikari.ShardReadyEvent) -> None:
    builder = (
        lavasnek_rs.LavalinkBuilder(event.my_user.id, "")
        .set_host(Config.LAVALINK_HOST)
        .set_password(Config.LAVALINK_PASSWORD)
    )

    builder.set_start_gateway(False)

    plugin.bot.d.lavalink = await builder.build(EventHandler())


@plugin.listener(hikari.VoiceStateUpdateEvent)
async def voice_state_update(event: hikari.VoiceStateUpdateEvent) -> None:
    plugin.bot.d.lavalink.raw_handle_event_voice_state_update(
        event.state.guild_id,
        event.state.user_id,
        event.state.session_id,
        event.state.channel_id,
    )


@plugin.listener(hikari.VoiceServerUpdateEvent)
async def voice_server_update(event: hikari.VoiceServerUpdateEvent) -> None:
    await plugin.bot.d.lavalink.raw_handle_event_voice_server_update(event.guild_id, event.endpoint, event.token)


@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("join", "Join the voice channel you are in.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_join(ctx: lightbulb.context.SlashContext) -> None:
    channel_id = await _join(ctx)

    if channel_id:
        await ctx.respond(f"Joined <#{channel_id}>.")


@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("leave", "Leave the voice channel the bot is in.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_leave(ctx: lightbulb.context.SlashContext) -> None:
    await plugin.bot.d.lavalink.destroy(ctx.guild_id)

    if ctx.guild_id is not None:
        await plugin.bot.update_voice_state(ctx.guild_id, None)
        await plugin.bot.d.lavalink.wait_for_connection_info_remove(ctx.guild_id)

    await plugin.bot.d.lavalink.remove_guild_node(ctx.guild_id)
    await plugin.bot.d.lavalink.remove_guild_from_loops(ctx.guild_id)

    await ctx.respond("Left voice channel.")


@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.option("query", "The query to search for.", modifier=lightbulb.OptionModifier.CONSUME_REST)
@lightbulb.command("play", "Search and play a song.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_play(ctx: lightbulb.context.SlashContext) -> None:
    query = ctx.options.query

    if not query:
        await ctx.respond("Please specify a query.")
        return

    con = plugin.bot.d.lavalink.get_guild_gateway_connection_info(ctx.guild_id)
    if not con:
        await _join(ctx)

    query_information = await plugin.bot.d.lavalink.auto_search_tracks(query)

    if not query_information.tracks:
        await ctx.respond("Could not find any video of the search query.")
        return
    try:
        await plugin.bot.d.lavalink.play(ctx.guild_id, query_information.tracks[0]).requester(ctx.author.id).queue()
    except lavasnek_rs.NoSessionPresent:
        await ctx.respond(f"Use /join first.")
        return
    await ctx.respond(f"Added `{query_information.tracks[0].info.title}` to the queue.")


@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("stop", "Stop the song.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_stop(ctx: lightbulb.context.SlashContext) -> None:
    await plugin.bot.d.lavalink.stop(ctx.guild_id)
    await ctx.respond("Stopped playing.")


@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("skip", "Skip the current song.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_skip(ctx: lightbulb.context.SlashContext) -> None:
    skip = await plugin.bot.d.lavalink.skip(ctx.guild_id)
    node = await plugin.bot.d.lavalink.get_guild_node(ctx.guild_id)

    if not skip:
        await ctx.respond("Nothing to skip.")
    else:
        if not node.queue and not node.now_playing:
            await plugin.bot.d.lavalink.stop(ctx.guild_id)

        await ctx.respond(f"Skipped {skip.track.info.title}.")


@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("pause", "Pause the song.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_pause(ctx: lightbulb.context.SlashContext) -> None:
    await plugin.bot.d.lavalink.pause(ctx.guild_id)
    await ctx.respond("Paused player.")


@plugin.command
@lightbulb.add_checks(lightbulb.guild_only)
@lightbulb.command("resume", "Resume the song.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_resume(ctx: lightbulb.context.SlashContext) -> None:
    await plugin.bot.d.lavalink.resume(ctx.guild_id)
    await ctx.respond("Resumed player.")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(plugin)
