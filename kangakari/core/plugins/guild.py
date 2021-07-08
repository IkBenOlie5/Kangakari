import hikari
import lightbulb
import sake


class Guild(lightbulb.plugins.Plugin):
    @lightbulb.group(name="prefix", aliases=["prefixes"])
    async def prefix_group(self, ctx: lightbulb.Context):
        prefixes = await ctx.bot.redis_cache.get_prefixes(ctx.guild_id)
        prefixes.append("@mention")
        await ctx.respond_embed(f"The current prefixes are: ```\n" + "\n".join(prefixes) + "```")

    @lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD)
    @prefix_group.command(name="add")
    async def prefix_add_command(self, ctx: lightbulb.Context, *, prefix: str):
        try:
            prefixes = await ctx.bot.redis_cache.get_prefixes(ctx.guild_id)
        except sake.errors.EntryNotFound:
            prefixes = await ctx.bot.db.column("SELECT prefix FROM prefixes WHERE guildid = $1", ctx.guild_id)
        if prefix in prefixes:
            return await ctx.respond_embed(f"Prefix `{prefix}` already exists.")
        prefixes.append(prefix)
        await ctx.bot.redis_cache.set_prefixes(ctx.guild_id, prefixes)
        await ctx.bot.db.execute("INSERT INTO prefixes (guildid, prefix) VALUES ($1, $2)", ctx.guild_id, prefix)
        await ctx.respond_embed(f"Succesfully added `{prefix}`.")

    @lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD)
    @prefix_group.command(name="remove", aliases=["delete"])
    async def prefix_remove_command(self, ctx: lightbulb.Context, *, prefix: str):
        try:
            prefixes = await ctx.bot.redis_cache.get_prefixes(ctx.guild_id)
        except sake.errors.EntryNotFound:
            prefixes = await ctx.bot.db.column("SELECT prefix FROM prefixes WHERE guildid = $1", ctx.guild_id)
        if prefix not in prefixes:
            return await ctx.respond_embed(f"Prefix `{prefix}` does not exist.")
        prefixes.remove(prefix)
        await ctx.bot.redis_cache.set_prefixes(ctx.guild_id, prefixes)
        await ctx.bot.db.execute("DELETE FROM prefixes WHERE guildid = $1 AND prefix = $2", ctx.guild_id, prefix)
        await ctx.respond_embed(f"Succesfully removed `{prefix}`.")


def load(bot: lightbulb.Bot):
    bot.add_plugin(Guild())


def unload(bot: lightbulb.Bot):
    bot.remove_plugin("Guild")
