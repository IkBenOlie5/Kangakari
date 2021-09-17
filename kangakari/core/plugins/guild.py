import typing

from hikari import Permissions
from lightbulb import Plugin
from lightbulb import checks
from lightbulb import commands
from sake.errors import EntryNotFound

if typing.TYPE_CHECKING:
    from lightbulb import Bot
    from lightbulb import Context


class Guild(Plugin):
    """Commands to setup the bot for your guild."""

    async def plugin_check(self, ctx: "Context") -> bool:
        if ctx.guild_id is None:
            await ctx.error("This command can only be executed inside servers.")
            return False
        return True

    @commands.group(name="prefix", aliases=["prefixes"])
    async def prefix_group(self, ctx: "Context") -> None:
        """The prefixes you currently have."""
        try:
            prefixes = await ctx.bot.redis_cache.get_prefixes(ctx.guild_id)
        except EntryNotFound:
            prefixes = []
        prefixes.append("@mention (can't be removed)")
        await ctx.info("The current prefixes are: ```\n" + "\n".join(prefixes) + "```")

    @checks.has_guild_permissions(Permissions.MANAGE_GUILD)
    @prefix_group.command(name="add")
    async def prefix_add_command(self, ctx: "Context", *, prefix: str) -> None:
        """Add a prefix to your guild."""
        await ctx.bot.redis_cache.add_prefixes(ctx.guild_id, prefix)
        await ctx.bot.db.execute(
            "UPDATE guilds SET prefixes = array_append(prefixes, $1) WHERE guild_id = $2", prefix, ctx.guild_id
        )
        await ctx.success(f"Successfully added `{prefix}`.")

    @checks.has_guild_permissions(Permissions.MANAGE_GUILD)
    @prefix_group.command(name="remove", aliases=["delete", "rm", "del"])
    async def prefix_remove_command(self, ctx: "Context", *, prefix: str) -> None:
        """Remove a prefix from your guild."""
        await ctx.bot.redis_cache.delete_prefixes(ctx.guild_id, prefix)
        await ctx.bot.db.execute(
            "UPDATE guilds SET prefixes = array_remove(prefixes, $1) WHERE guild_id = $2", prefix, ctx.guild_id
        )
        await ctx.success(f"Successfully removed `{prefix}`.")


def load(bot: "Bot") -> None:
    bot.add_plugin(Guild())


def unload(bot: "Bot") -> None:
    bot.remove_plugin("Guild")
