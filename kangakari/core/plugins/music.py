import logging
import typing

import lavasnek_rs
from hikari import VoiceServerUpdateEvent
from hikari import VoiceStateUpdateEvent
from lightbulb import Plugin
from lightbulb import commands
from lightbulb import listener

if typing.TYPE_CHECKING:
    from hikari import Snowflake

    from kangakari import Bot
    from kangakari.core import Context


class EventHandler:
    """Events from the Lavalink server"""

    async def track_start(self, _: lavasnek_rs.Lavalink, event: lavasnek_rs.TrackStart) -> None:
        logging.info("Track started on guild: %s", event.guild_id)

    async def track_finish(self, _: lavasnek_rs.Lavalink, event: lavasnek_rs.TrackFinish) -> None:
        logging.info("Track finished on guild: %s", event.guild_id)

    async def track_exception(self, lavalink: lavasnek_rs.Lavalink, event: lavasnek_rs.TrackException) -> None:
        logging.warning("Track exception event happened on guild: %d", event.guild_id)

        skip = await lavalink.skip(event.guild_id)
        node = await lavalink.get_guild_node(event.guild_id)

        if skip:
            if not node.queue and not node.now_playing:
                await lavalink.stop(event.guild_id)


class Music(Plugin):
    __slots__ = ("bot",)

    def __init__(self, bot: "Bot") -> None:
        super().__init__()
        self.bot = bot

    async def plugin_check(self, ctx: "Context") -> bool:
        if ctx.guild_id is None:
            await ctx.error("This command can only be executed inside servers.")
            return False
        return True

    @listener(VoiceStateUpdateEvent)
    async def on_voice_state_update(self, e: VoiceStateUpdateEvent) -> None:
        await self.bot.lavalink.raw_handle_event_voice_state_update(
            e.state.guild_id,
            e.state.user_id,
            e.state.session_id,
            e.state.channel_id,
        )

        if e.old_state is None:
            return
        states = self.bot.cache.get_voice_states_view_for_channel(e.guild_id, e.old_state.channel_id)
        if len(states) == 1 and states.get_item_at(0).user_id == self.bot.get_me().id:
            await self._leave(e.guild_id)

    @listener(VoiceServerUpdateEvent)
    async def on_voice_server_update(self, e: VoiceServerUpdateEvent) -> None:
        await self.bot.lavalink.raw_handle_event_voice_server_update(e.guild_id, e.endpoint, e.token)

    async def _join(self, ctx: "Context") -> typing.Optional["Snowflake"]:
        states = self.bot.cache.get_voice_states_view_for_guild(ctx.guild_id)
        voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == ctx.author.id)]

        if not voice_state:
            await ctx.warning("Connect to a voice channel first.")
            return None

        channel_id = voice_state[0].channel_id

        await self.bot.update_voice_state(ctx.guild_id, channel_id, self_deaf=True)
        connection_info = await self.bot.lavalink.wait_for_full_connection_info_insert(ctx.guild_id)
        await ctx.bot.lavalink.create_session(connection_info)

        return channel_id

    async def _leave(self, guild_id: "Snowflake") -> None:
        await self.bot.lavalink.destroy(guild_id)

        await self.bot.update_voice_state(guild_id, None)
        await self.bot.lavalink.wait_for_connection_info_remove(guild_id)

        await self.bot.lavalink.remove_guild_node(guild_id)
        await self.bot.lavalink.remove_guild_from_loops(guild_id)

    @commands.command(name="join", aliases=["connect"])
    async def join_command(self, ctx: "Context") -> None:
        """Join a channel."""
        channel_id = await self._join(ctx)

        if channel_id:
            await ctx.success(f"Joined <#{channel_id}>.")

    @commands.command(name="leave", aliases=["disconnect"])
    async def leave_command(self, ctx: "Context") -> None:
        """Leave a chennel."""
        await self._leave(ctx.guild_id)

        await ctx.success("Left voice channel.")

    @commands.command(name="play")
    async def play_command(self, ctx: "Context", *, query: str) -> None:
        """Play a Song."""
        cxn = await self.bot.lavalink.get_guild_gateway_connection_info(ctx.guild_id)
        if not cxn:
            await self._join(ctx)

        query_info = await self.bot.lavalink.auto_search_tracks(query)

        if not query_info.tracks:
            await ctx.warning("Could not find any video of the search query.")
            return

        await self.bot.lavalink.play(ctx.guild_id, query_info.tracks[0]).requester(ctx.author.id).queue()

        await ctx.success(f"Added to queue: {query_info.tracks[0].info.title}.")


def load(bot: "Bot") -> None:
    bot.add_plugin(Music(bot))


def unload(bot: "Bot") -> None:
    bot.remove_plugin("Music")
