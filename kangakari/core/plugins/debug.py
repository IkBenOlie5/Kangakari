import logging
import typing

from lightbulb import Plugin
from lightbulb import checks
from lightbulb import commands
from lightbulb import errors

if typing.TYPE_CHECKING:
    from kangakari.core import Bot
    from kangakari.utils import Context


class Debug(Plugin):
    """Utility commands only accessible by the owner."""

    async def handle_plugins(self, ctx: "Context", plugin_string: str, action: str) -> None:
        if plugin_string:
            plugins = plugin_string.split(" ")
        else:
            plugins = [e.split(".")[-1] for e in ctx.bot.plugins]

        count = 0
        for plugin in plugins:
            try:
                getattr(ctx.bot, f"{action}_extension")(f"kangakari.core.plugins.{plugin.lower()}")
                logging.info(f"Plugin '{plugin}' has been {action}ed.")
                count += 1
            except errors.ExtensionAlreadyLoaded:
                logging.error(f"Plugin '{plugin}' is already loaded.")
            except errors.ExtensionNotLoaded:
                logging.error(f"Plugin '{plugin}' is not currently loaded.")

        await ctx.success(f"{count} extension(s) {action}ed.")

    @checks.owner_only()
    @commands.command(name="reload", hidden=True)
    async def reload_command(self, ctx: "Context", *, plugins: str = "") -> None:
        """Reload cogs."""
        await self.handle_plugins(ctx, plugins, "reload")

    @checks.owner_only()
    @commands.command(name="load", hidden=True)
    async def load_command(self, ctx: "Context", *, plugins: str = "") -> None:
        """Load cogs."""
        await self.handle_plugins(ctx, plugins, "load")

    @checks.owner_only()
    @commands.command(name="unload", hidden=True)
    async def unload_command(self, ctx: "Context", *, plugins: str = "") -> None:
        """Unload cogs."""
        await self.handle_plugins(ctx, plugins, "unload")

    @checks.owner_only()
    @commands.command(name="shutdown", hidden=True)
    async def shutdown_command(self, ctx: "Context") -> None:
        """Shut the bot down."""
        await ctx.info("Shutting down.")
        await ctx.bot.close()


def load(bot: "Bot") -> None:
    bot.add_plugin(Debug())


def unload(bot: "Bot") -> None:
    bot.remove_plugin("Debug")
