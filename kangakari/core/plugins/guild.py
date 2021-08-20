import hikari
import lightbulb
import sake


class Guild(lightbulb.plugins.Plugin):
    """Commands to setup the bot for your guild."""

    async def plugin_check(self, ctx: lightbulb.Context) -> bool:
        if ctx.guild_id is None:
            await ctx.respond_embed("This command can only be executed inside servers.")
            return False
        return True

    @lightbulb.group(name="prefix", aliases=["prefixes"])
    async def prefix_group(self, ctx: lightbulb.Context) -> None:
        """The prefixes you currently have."""
        try:
            prefixes = await ctx.bot.redis_cache.get_prefixes(ctx.guild_id)
        except sake.errors.EntryNotFound:
            prefixes = []
        prefixes.append("@mention (can't be removed)")
        await ctx.respond_embed("The current prefixes are: ```\n" + "\n".join(prefixes) + "```")

    @lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD)
    @prefix_group.command(name="add")
    async def prefix_add_command(self, ctx: lightbulb.Context, *, prefix: str) -> None:
        """Add a prefix to your guild."""
        await ctx.bot.redis_cache.add_prefixes(ctx.guild_id, prefix)
        await ctx.bot.db.execute(
            "UPDATE guilds SET prefixes = array_append(prefixes, $1) WHERE guildid = $2", prefix, ctx.guild_id
        )
        await ctx.respond_embed(f"Successfully added `{prefix}`.")

    @lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD)
    @prefix_group.command(name="remove", aliases=["delete"])
    async def prefix_remove_command(self, ctx: lightbulb.Context, *, prefix: str) -> None:
        """Remove a prefix from your guild."""
        await ctx.bot.redis_cache.delete_prefixes(ctx.guild_id, prefix)
        await ctx.bot.db.execute(
            "UPDATE guilds SET prefixes = array_remove(prefixes, $1) WHERE guildid = $2", prefix, ctx.guild_id
        )
        await ctx.respond_embed(f"Successfully removed `{prefix}`.")


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Guild())


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Guild")
