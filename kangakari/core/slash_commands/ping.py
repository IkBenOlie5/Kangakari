import typing

if typing.TYPE_CHECKING:
    from kangakari import Bot

from lightbulb import slash_commands

from kangakari.core import config


class Ping(slash_commands.SlashCommand):
    description = "test"
    enabled_guilds = (config.TEST_GUILD_ID,)

    async def callback(self, ctx: slash_commands.SlashCommandContext) -> None:
        await ctx.respond("pong")


def load(bot: "Bot") -> None:
    bot.add_slash_command(Ping)


def unload(bot: "Bot") -> None:
    bot.remove_slash_command("Ping")
