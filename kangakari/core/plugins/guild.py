import hikari
import lightbulb


class Guild(lightbulb.plugins.Plugin):
    @lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD)
    @lightbulb.command(name="change_prefix")
    async def change_prefix_command(self, ctx: lightbulb.Context, prefix: str):
        await ctx.bot.db.execute("UPDATE guilds SET prefix = $1 WHERE guildid = $2", prefix, ctx.guild.id)
        await ctx.bot.prefix_cache.set(ctx.guild.id, prefix)
        await ctx.respond_embed(f"Changed server prefix to `{prefix}`.")

    @lightbulb.command(name="current_prefix", aliases=["cp", "prefix"])
    async def current_prefix_command(self, ctx: lightbulb.Context):
        prefix = await ctx.bot.prefix_cache.get(ctx.guild.id)
        await ctx.respond_embed(f"The current prefix is `{prefix}`.")


def load(bot: lightbulb.Bot):
    bot.add_plugin(Guild())


def unload(bot: lightbulb.Bot):
    bot.remove_plugin("Guild")
