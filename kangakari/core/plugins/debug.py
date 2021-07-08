import logging

import lightbulb


class Debug(lightbulb.plugins.Plugin):
    """Utility commands only accesible by the owner."""

    async def handle_plugins(self, ctx: lightbulb.Context, plugin_string: str, action: str) -> None:
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
            except lightbulb.errors.ExtensionAlreadyLoaded:
                logging.error(f"Plugin '{plugin}' is already loaded.")
            except lightbulb.errors.ExtensionNotLoaded:
                logging.error(f"Plugin '{plugin}' is not currently loaded.")

        await ctx.respond_embed(f"{count} extension(s) {action}ed.")

    @lightbulb.checks.owner_only()
    @lightbulb.commands.command(name="reload", hidden=True)
    async def reload_command(self, ctx: lightbulb.Context, *, plugins: str = ""):
        """Reload cogs."""
        await self.handle_plugins(ctx, plugins, "reload")

    @lightbulb.checks.owner_only()
    @lightbulb.commands.command(name="load", hidden=True)
    async def load_command(self, ctx: lightbulb.Context, *, plugins: str = ""):
        """Load cogs."""
        await self.handle_plugins(ctx, plugins, "load")

    @lightbulb.checks.owner_only()
    @lightbulb.commands.command(name="unload", hidden=True)
    async def unload_command(self, ctx: lightbulb.Context, *, plugins: str = ""):
        """Unload cogs."""
        await self.handle_plugins(ctx, plugins, "unload")

    @lightbulb.checks.owner_only()
    @lightbulb.commands.command(name="shutdown", hidden=True)
    async def shutdown_command(self, ctx: lightbulb.Context):
        """Shut the bot down."""
        await ctx.respond_embed("Shutting down.")
        await ctx.bot.close()


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Debug())


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Debug")
