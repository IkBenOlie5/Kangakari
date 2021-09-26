import logging
import typing

import lavasnek_rs
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

    async def track_start(self, _, e):
        logging.info("Track started on guild: %s", e.guild_id)

    async def track_finish(self, _, e):
        logging.info("Track finished on guild: %s", e.guild_id)


class Music(Plugin):
    def __init__(self, bot: "Bot") -> None:
        super().__init__()
        self.bot = bot

    async def _join(self, ctx: "Context") -> typing.Optional["Snowflake"]:
        states = ctx.bot.cache.get_voice_states_view_for_guild(ctx.guild_id)
        voice_state = list(filter(lambda i: i.user_id == ctx.author.id, states.iterator()))

        if not voice_state:
            await ctx.warning("Connect to a voice channel first.")
            return

        channel_id = voice_state[0].channel_id
        connection_info = await ctx.bot.lavalink.join(ctx.guild_id, channel_id)
        await ctx.bot.lavalink.create_session(connection_info)

        return channel_id

    async def _leave(self, guild_id: "Snowflake") -> None:
        await self.bot.lavalink.destroy(guild_id)
        await self.bot.lavalink.leave(guild_id)

        await self.bot.lavalink.remove_guild_node(guild_id)
        await self.bot.lavalink.remove_guild_from_loops(guild_id)

    @listener(event_type=VoiceStateUpdateEvent)
    async def on_voice_state_update(self, e: VoiceStateUpdateEvent) -> None:
        if e.old_state is None:
            return
        states = self.bot.cache.get_voice_states_view_for_channel(e.guild_id, e.old_state.channel_id)
        if any(states[state].user_id == self.bot.get_me().id for state in states) and len(states) == 1:
            self._leave(e.guild_id)

    @commands.command(name="join", aliases=["connect"])
    async def join_command(self, ctx: "Context") -> None:
        channel_id = await self._join(ctx)

        if channel_id:
            await ctx.success(f"Joined <#{channel_id}>.")

    @commands.command(name="leave", aliases=["disconnect"])
    async def leave_command(self, ctx: "Context") -> None:
        await self._leave(ctx.guild_id)

        await ctx.success("Left voice channel.")


def load(bot: "Bot") -> None:
    bot.add_plugin(Music(bot))


def unload(bot: "Bot") -> None:
    bot.remove_plugin("Music")
