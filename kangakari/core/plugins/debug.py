import logging

import lightbulb


class Debug(lightbulb.plugins.Plugin):
    async def handle_plugins(self, ctx: lightbulb.Context, plugins: str, action: str) -> None:
        if plugins:
            plugins = plugins.split(" ")
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

        await ctx.respond(f"{count} extension(s) {action}ed.")

    @lightbulb.checks.owner_only()
    @lightbulb.commands.command(name="reload")
    async def reload_command(self, ctx, *, plugins=""):
        await self.handle_plugins(ctx, plugins, "reload")

    @lightbulb.checks.owner_only()
    @lightbulb.commands.command(name="load")
    async def load_command(self, ctx, *, plugins=""):
        await self.handle_plugins(ctx, plugins, "load")

    @lightbulb.checks.owner_only()
    @lightbulb.commands.command(name="unload")
    async def unload_command(self, ctx, *, plugins=""):
        await self.handle_plugins(ctx, plugins, "unload")

    @lightbulb.checks.owner_only()
    @lightbulb.commands.command(name="shutdown")
    async def shutdown_command(self, ctx):
        await ctx.respond("Shutting down.")
        await ctx.bot.close(force=True)


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Debug())


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Debug")
